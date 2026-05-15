"""
Core disk-scanning and cleaning logic.
All operations are Windows-specific.
"""
import os
import shutil
import ctypes
import subprocess
from dataclasses import dataclass, field
from typing import Callable, List, Optional, Tuple


# ---------------------------------------------------------------------------
# Utilities
# ---------------------------------------------------------------------------

def format_bytes(size: int) -> str:
    """Convert bytes to a human-readable string."""
    if size < 1024:
        return f"{size} B"
    elif size < 1024 ** 2:
        return f"{size / 1024:.1f} KB"
    elif size < 1024 ** 3:
        return f"{size / 1024 ** 2:.1f} MB"
    else:
        return f"{size / 1024 ** 3:.2f} GB"


def get_dir_size(path: str) -> Tuple[int, int]:
    """Return (total_bytes, file_count) for a directory tree."""
    total, count = 0, 0
    try:
        for root, _dirs, files in os.walk(path):
            for name in files:
                try:
                    total += os.path.getsize(os.path.join(root, name))
                    count += 1
                except OSError:
                    pass
    except OSError:
        pass
    return total, count


def get_disk_usage(drive: str = "C:\\") -> Tuple[int, int, int]:
    """Return (total, used, free) bytes for *drive*."""
    try:
        u = shutil.disk_usage(drive)
        return u.total, u.used, u.free
    except Exception:
        return 0, 0, 0


def is_admin() -> bool:
    """Return True if the process has administrator privileges."""
    try:
        return bool(ctypes.windll.shell32.IsUserAnAdmin())
    except Exception:
        return False


# ---------------------------------------------------------------------------
# Data model
# ---------------------------------------------------------------------------

@dataclass
class CleanItem:
    path: str
    size: int = 0
    is_dir: bool = False


@dataclass
class CleanCategory:
    id: str
    name: str
    description: str
    items: List[CleanItem] = field(default_factory=list)
    total_size: int = 0
    file_count: int = 0
    enabled: bool = True
    error: str = ""

    def size_str(self) -> str:
        return format_bytes(self.total_size)


# ---------------------------------------------------------------------------
# Main cleaner class
# ---------------------------------------------------------------------------

class DiskCleaner:
    """Scan and clean common junk locations on Windows C: drive."""

    #: (id, display_name, description)
    CATEGORIES: List[Tuple[str, str, str]] = [
        ("user_temp",     "用户临时文件",      "用户临时目录 (%TEMP%) 中的残留临时文件"),
        ("windows_temp",  "Windows 临时文件",  "C:\\Windows\\Temp 系统临时目录"),
        ("windows_upd",   "Windows 更新缓存",  "Windows Update 下载缓存（已安装更新不受影响）"),
        ("windows_old",   "Windows.old",       "系统升级遗留的旧系统目录"),
        ("recycle_bin",   "回收站",            "所有驱动器回收站中已删除的文件"),
        ("chrome_cache",  "Chrome 缓存",       "Google Chrome 浏览器缓存与代码缓存"),
        ("edge_cache",    "Edge 缓存",         "Microsoft Edge 浏览器缓存与代码缓存"),
        ("firefox_cache", "Firefox 缓存",      "Mozilla Firefox 浏览器 cache2 缓存"),
        ("thumbnail",     "缩略图缓存",        "Windows 资源管理器缩略图数据库文件"),
        ("win_logs",      "Windows 日志",      "C:\\Windows\\Logs 系统日志文件"),
        ("prefetch",      "预读取缓存",        "Windows Prefetch 文件（清理后首次启动程序稍慢）"),
        ("error_rep",     "错误报告存档",      "Windows 错误报告存档与队列文件"),
        ("delivery_opt",  "传递优化缓存",      "Windows Update 传递优化下载缓存"),
        ("hiberfil",      "休眠文件",          "C:\\hiberfil.sys，关闭休眠后可释放"),
        ("pagefile",      "页面文件",          "C:\\pagefile.sys / C:\\swapfile.sys，仅分析"),
        ("memory_dump",   "内存转储",          "C:\\Windows\\MEMORY.DMP 崩溃转储文件"),
        ("minidump",      "小型转储",          "C:\\Windows\\Minidump 崩溃转储目录"),
        ("winsxs",        "WinSxS 组件存储",   "系统组件存储，仅分析，不直接删除"),
    ]

    def __init__(self) -> None:
        self.categories: List[CleanCategory] = []

    # ------------------------------------------------------------------
    # Scanning
    # ------------------------------------------------------------------

    def scan(self, on_progress: Optional[Callable[[float, str], None]] = None
             ) -> List[CleanCategory]:
        """Scan all categories and return results."""
        scanners = {
            "user_temp":     self._scan_user_temp,
            "windows_temp":  self._scan_windows_temp,
            "windows_upd":   self._scan_windows_update,
            "windows_old":   self._scan_windows_old,
            "recycle_bin":   self._scan_recycle_bin,
            "chrome_cache":  self._scan_chrome,
            "edge_cache":    self._scan_edge,
            "firefox_cache": self._scan_firefox,
            "thumbnail":     self._scan_thumbnails,
            "win_logs":      self._scan_win_logs,
            "prefetch":      self._scan_prefetch,
            "error_rep":     self._scan_error_reports,
            "delivery_opt":  self._scan_delivery_opt,
            "hiberfil":      self._scan_hiberfil,
            "pagefile":      self._scan_pagefile,
            "memory_dump":   self._scan_memory_dump,
            "minidump":      self._scan_minidump,
            "winsxs":        self._scan_winsxs,
        }

        self.categories = []
        n = len(self.CATEGORIES)
        for i, (cat_id, name, desc) in enumerate(self.CATEGORIES):
            if on_progress:
                on_progress(i / n, f"扫描中: {name}")
            cat = CleanCategory(id=cat_id, name=name, description=desc)
            if cat_id in {"pagefile", "winsxs"}:
                cat.enabled = False
            try:
                scanners[cat_id](cat)
            except Exception as exc:
                cat.error = str(exc)
            self.categories.append(cat)

        if on_progress:
            on_progress(1.0, "扫描完成")
        return self.categories

    # helpers ---------------------------------------------------------------

    def _add_dir(self, cat: CleanCategory, path: str) -> None:
        p = os.path.expandvars(path)
        if os.path.isdir(p) and not self._path_exists(cat, p):
            sz, cnt = get_dir_size(p)
            cat.items.append(CleanItem(p, sz, True))
            cat.total_size += sz
            cat.file_count += cnt

    def _add_file(self, cat: CleanCategory, path: str) -> None:
        p = os.path.expandvars(path)
        if os.path.isfile(p) and not self._path_exists(cat, p):
            try:
                sz = os.path.getsize(p)
                cat.items.append(CleanItem(p, sz, False))
                cat.total_size += sz
                cat.file_count += 1
            except OSError:
                pass

    @staticmethod
    def _path_exists(cat: CleanCategory, path: str) -> bool:
        target = os.path.normcase(os.path.normpath(path))
        for item in cat.items:
            if os.path.normcase(os.path.normpath(item.path)) == target:
                return True
        return False

    # category scanners -----------------------------------------------------

    def _scan_user_temp(self, cat: CleanCategory) -> None:
        self._add_dir(cat, "%TEMP%")

    def _scan_windows_temp(self, cat: CleanCategory) -> None:
        self._add_dir(cat, r"C:\Windows\Temp")

    def _scan_windows_update(self, cat: CleanCategory) -> None:
        self._add_dir(cat, r"C:\Windows\SoftwareDistribution\Download")

    def _scan_windows_old(self, cat: CleanCategory) -> None:
        self._add_dir(cat, r"C:\Windows.old")

    def _scan_recycle_bin(self, cat: CleanCategory) -> None:
        for letter in "CDEFGHIJKLMNOPQRSTUVWXYZ":
            path = f"{letter}:\\$Recycle.Bin"
            if os.path.exists(path):
                sz, cnt = get_dir_size(path)
                if sz > 0 or cnt > 0:
                    cat.items.append(CleanItem(path, sz, True))
                    cat.total_size += sz
                    cat.file_count += cnt

    def _scan_browser(self, cat: CleanCategory, subdirs: List[str]) -> None:
        local = os.environ.get("LOCALAPPDATA", "")
        for subdir in subdirs:
            self._add_dir(cat, os.path.join(local, subdir))

    def _scan_chromium_user_data(self, cat: CleanCategory, base: str) -> None:
        root_cache_dirs = [
            "BrowserMetrics",
            "DeferredBrowserMetrics",
            "component_crx_cache",
            "extensions_crx_cache",
        ]
        profile_cache_dirs = [
            r"Cache",
            r"Code Cache",
            r"GPUCache",
            r"ShaderCache",
            r"GrShaderCache",
            r"GraphiteDawnCache",
            r"DawnCache",
            r"Media Cache",
            r"Service Worker\CacheStorage",
            r"Service Worker\ScriptCache",
        ]

        for rel in root_cache_dirs:
            self._add_dir(cat, os.path.join(base, rel))

        if not os.path.isdir(base):
            return

        for name in os.listdir(base):
            if name == "Default" or name.startswith("Profile") or name in {"Guest Profile", "System Profile"}:
                profile = os.path.join(base, name)
                if os.path.isdir(profile):
                    for rel in profile_cache_dirs:
                        self._add_dir(cat, os.path.join(profile, rel))

    def _scan_chrome(self, cat: CleanCategory) -> None:
        base = os.path.join(os.environ.get("LOCALAPPDATA", ""), r"Google\Chrome\User Data")
        self._scan_chromium_user_data(cat, base)

    def _scan_edge(self, cat: CleanCategory) -> None:
        base = os.path.join(os.environ.get("LOCALAPPDATA", ""), r"Microsoft\Edge\User Data")
        self._scan_chromium_user_data(cat, base)

    def _scan_firefox(self, cat: CleanCategory) -> None:
        for env_key in ("APPDATA", "LOCALAPPDATA"):
            base = os.path.join(os.environ.get(env_key, ""),
                                r"Mozilla\Firefox\Profiles")
            if os.path.isdir(base):
                for profile in os.listdir(base):
                    self._add_dir(cat, os.path.join(base, profile, "cache2"))

    def _scan_thumbnails(self, cat: CleanCategory) -> None:
        explorer = os.path.join(
            os.environ.get("LOCALAPPDATA", ""),
            r"Microsoft\Windows\Explorer",
        )
        if os.path.isdir(explorer):
            for fname in os.listdir(explorer):
                if fname.startswith("thumbcache_") and fname.endswith(".db"):
                    self._add_file(cat, os.path.join(explorer, fname))

    def _scan_win_logs(self, cat: CleanCategory) -> None:
        self._add_dir(cat, r"C:\Windows\Logs")

    def _scan_prefetch(self, cat: CleanCategory) -> None:
        self._add_dir(cat, r"C:\Windows\Prefetch")

    def _scan_error_reports(self, cat: CleanCategory) -> None:
        local = os.environ.get("LOCALAPPDATA", "")
        for path in [
            r"C:\ProgramData\Microsoft\Windows\WER\ReportArchive",
            r"C:\ProgramData\Microsoft\Windows\WER\ReportQueue",
            os.path.join(local, r"Microsoft\Windows\WER\ReportArchive"),
            os.path.join(local, r"Microsoft\Windows\WER\ReportQueue"),
        ]:
            self._add_dir(cat, path)

    def _scan_delivery_opt(self, cat: CleanCategory) -> None:
        for path in [
            r"C:\ProgramData\Microsoft\Windows\DeliveryOptimization\Cache",
            r"C:\Windows\ServiceProfiles\NetworkService\AppData\Local\Microsoft\Windows\DeliveryOptimization\Cache",
            r"C:\Windows\SoftwareDistribution\DeliveryOptimization",
        ]:
            self._add_dir(cat, path)

    def _scan_hiberfil(self, cat: CleanCategory) -> None:
        self._add_file(cat, r"C:\hiberfil.sys")

    def _scan_pagefile(self, cat: CleanCategory) -> None:
        self._add_file(cat, r"C:\pagefile.sys")
        self._add_file(cat, r"C:\swapfile.sys")

    def _scan_memory_dump(self, cat: CleanCategory) -> None:
        self._add_file(cat, r"C:\Windows\MEMORY.DMP")

    def _scan_minidump(self, cat: CleanCategory) -> None:
        self._add_dir(cat, r"C:\Windows\Minidump")

    def _scan_winsxs(self, cat: CleanCategory) -> None:
        self._add_dir(cat, r"C:\Windows\WinSxS")

    # ------------------------------------------------------------------
    # Cleaning
    # ------------------------------------------------------------------

    def clean(
        self,
        category_ids: List[str],
        on_progress: Optional[Callable[[float, str], None]] = None,
        on_log: Optional[Callable[[str], None]] = None,
    ) -> Tuple[int, int]:
        """Clean selected categories. Returns (bytes_freed, files_removed)."""
        targets = [c for c in self.categories
                   if c.id in category_ids and c.total_size > 0 and c.enabled]
        if not targets:
            return 0, 0

        total_freed, total_files = 0, 0
        n = len(targets)
        for i, cat in enumerate(targets):
            if on_progress:
                on_progress(i / n, f"清理中: {cat.name}")
            freed, files = self._clean_category(cat, on_log)
            total_freed += freed
            total_files += files

        if on_progress:
            on_progress(1.0, "清理完成")
        return total_freed, total_files

    def _clean_category(
        self,
        cat: CleanCategory,
        on_log: Optional[Callable[[str], None]],
    ) -> Tuple[int, int]:
        freed, files = 0, 0

        if cat.id == "recycle_bin":
            try:
                # SHERB_NOCONFIRMATION | SHERB_NOPROGRESSUI | SHERB_NOSOUND
                ctypes.windll.shell32.SHEmptyRecycleBinW(None, None, 0x0007)
                freed = cat.total_size
                files = cat.file_count
                if on_log:
                    on_log(f"[OK] 回收站已清空 (释放 {format_bytes(freed)})")
            except Exception as exc:
                if on_log:
                    on_log(f"[错误] 清空回收站失败: {exc}")
            return freed, files

        if cat.id == "hiberfil":
            try:
                result = subprocess.run(
                    ["powercfg", "/h", "off"],
                    capture_output=True,
                    text=True,
                )
                if result.returncode != 0:
                    raise RuntimeError(
                        (result.stderr or result.stdout or "").strip()
                        or f"powercfg exited with code {result.returncode}"
                    )
                freed = cat.total_size
                files = cat.file_count or 1
                if on_log:
                    on_log(f"[OK] 已关闭休眠并释放 {format_bytes(freed)}")
            except Exception as exc:
                if on_log:
                    on_log(f"[错误] 关闭休眠失败: {exc}")
            return freed, files

        for item in cat.items:
            if item.is_dir:
                f, c = self._clean_dir_contents(item.path, on_log)
                freed += f
                files += c
            else:
                try:
                    sz = os.path.getsize(item.path)
                    os.remove(item.path)
                    freed += sz
                    files += 1
                    if on_log:
                        on_log(f"[OK] 删除: {item.path} ({format_bytes(sz)})")
                except Exception as exc:
                    if on_log:
                        on_log(f"[跳过] {item.path}: {exc}")

        return freed, files

    @staticmethod
    def _clean_dir_contents(
        path: str,
        on_log: Optional[Callable[[str], None]],
    ) -> Tuple[int, int]:
        freed, files = 0, 0
        try:
            for entry in os.scandir(path):
                try:
                    if entry.is_dir(follow_symlinks=False):
                        sz, cnt = get_dir_size(entry.path)
                        shutil.rmtree(entry.path, ignore_errors=True)
                        freed += sz
                        files += cnt
                        if on_log:
                            on_log(
                                f"[OK] 删除目录: {entry.path}"
                                f" ({format_bytes(sz)}, {cnt} 文件)"
                            )
                    else:
                        sz = entry.stat().st_size
                        os.remove(entry.path)
                        freed += sz
                        files += 1
                        if on_log:
                            on_log(f"[OK] 删除: {entry.path} ({format_bytes(sz)})")
                except Exception as exc:
                    if on_log:
                        on_log(f"[跳过] {entry.path}: {exc}")
        except PermissionError as exc:
            if on_log:
                on_log(f"[权限] 无法访问 {path}: {exc}")
        return freed, files
