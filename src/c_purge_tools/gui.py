"""
Tkinter GUI for the C: disk cleaner.
"""
import threading
import tkinter as tk
from tkinter import messagebox, scrolledtext, ttk
from typing import Dict, List

from .cleaner import DiskCleaner, format_bytes, get_disk_usage, is_admin
from .config import Config

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

APP_TITLE   = "C-PurgeTools"
APP_VERSION = "v1.0"

CHECKED   = "☑"
UNCHECKED = "☐"

ACCENT   = "#0078d4"
SUCCESS  = "#107c10"
WARNING  = "#ca5010"
DANGER   = "#d83b01"
HEADER_BG = "#003d73"
HEADER_FG = "#ffffff"


# ---------------------------------------------------------------------------
# App
# ---------------------------------------------------------------------------

class CleanerApp:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.cleaner = DiskCleaner()
        self.config = Config()
        self._checked: Dict[str, bool] = {}
        self._scanning = False
        self._cleaning = False

        self._setup_window()
        self._apply_style()
        self._build_ui()
        self._refresh_disk_info()

    # ------------------------------------------------------------------
    # Window / style
    # ------------------------------------------------------------------

    def _setup_window(self) -> None:
        self.root.title(f"{APP_TITLE} {APP_VERSION}")
        self.root.geometry("1040x720")
        self.root.minsize(920, 620)
        self.root.configure(bg="#f0f0f0")

    def _apply_style(self) -> None:
        s = ttk.Style()
        s.theme_use("clam")

        s.configure("TFrame",       background="#f0f0f0")
        s.configure("TLabelframe",  background="#f0f0f0")
        s.configure("TLabelframe.Label",
                    background="#f0f0f0",
                    font=("Microsoft YaHei UI", 9, "bold"),
                    foreground="#444444")
        s.configure("TLabel",       background="#f0f0f0",
                    font=("Microsoft YaHei UI", 9))
        s.configure("TCheckbutton", background="#f0f0f0",
                    font=("Microsoft YaHei UI", 9))

        s.configure("Accent.TButton",
                    font=("Microsoft YaHei UI", 10, "bold"),
                    foreground="white",
                    background=ACCENT,
                    borderwidth=0,
                    padding=(12, 6))
        s.map("Accent.TButton",
              background=[("active", "#005a9e"), ("disabled", "#aaaaaa")],
              foreground=[("disabled", "#dddddd")])

        s.configure("Danger.TButton",
                    font=("Microsoft YaHei UI", 10, "bold"),
                    foreground="white",
                    background=DANGER,
                    borderwidth=0,
                    padding=(12, 6))
        s.map("Danger.TButton",
              background=[("active", "#a02800"), ("disabled", "#aaaaaa")],
              foreground=[("disabled", "#dddddd")])

        s.configure("Treeview",
                    rowheight=26,
                    font=("Microsoft YaHei UI", 9))
        s.configure("Treeview.Heading",
                    font=("Microsoft YaHei UI", 9, "bold"),
                    background="#e0e0e0",
                    foreground="#333333")
        s.map("Treeview",
              background=[("selected", "#cce4f7")],
              foreground=[("selected", "#000000")])

    # ------------------------------------------------------------------
    # UI construction
    # ------------------------------------------------------------------

    def _build_ui(self) -> None:
        self._build_header()
        content = ttk.Frame(self.root, padding="12")
        content.pack(fill=tk.BOTH, expand=True)
        self._build_disk_info(content)
        self._build_category_list(content)
        self._build_buttons(content)
        self._build_progress(content)
        self._build_log(content)

    # header ----------------------------------------------------------------

    def _build_header(self) -> None:
        bar = tk.Frame(self.root, bg=HEADER_BG, height=56)
        bar.pack(fill=tk.X)
        bar.pack_propagate(False)

        tk.Label(
            bar,
            text=f"  C盘清理工具",
            font=("Microsoft YaHei UI", 16, "bold"),
            bg=HEADER_BG, fg=HEADER_FG,
        ).pack(side=tk.LEFT, padx=(18, 4), pady=10)

        tk.Label(
            bar,
            text=APP_VERSION,
            font=("Microsoft YaHei UI", 9),
            bg=HEADER_BG, fg="#8ab4d4",
        ).pack(side=tk.LEFT, pady=(16, 0))

        admin_text  = "✓ 管理员模式" if is_admin() else "⚠ 普通用户模式"
        admin_color = "#90ee90"     if is_admin() else "#ffcc80"
        tk.Label(
            bar, text=admin_text,
            font=("Microsoft YaHei UI", 9),
            bg=HEADER_BG, fg=admin_color,
        ).pack(side=tk.RIGHT, padx=18)

    # disk info -------------------------------------------------------------

    def _build_disk_info(self, parent: ttk.Frame) -> None:
        frame = ttk.LabelFrame(parent, text="C: 磁盘信息", padding="10")
        frame.pack(fill=tk.X, pady=(0, 10))

        # metric labels
        metrics = ttk.Frame(frame)
        metrics.pack(fill=tk.X)
        self._disk_labels: Dict[str, ttk.Label] = {}
        for key, caption in [("total", "总容量"), ("used", "已使用"), ("free", "可用空间")]:
            box = ttk.Frame(metrics)
            box.pack(side=tk.LEFT, padx=(0, 40))
            ttk.Label(box, text=caption,
                      foreground="#888888",
                      font=("Microsoft YaHei UI", 8)).pack(anchor="w")
            lbl = ttk.Label(box, text="--",
                            font=("Microsoft YaHei UI", 13, "bold"))
            lbl.pack(anchor="w")
            self._disk_labels[key] = lbl

        # usage bar
        bar_row = ttk.Frame(frame)
        bar_row.pack(fill=tk.X, pady=(8, 0))
        ttk.Label(bar_row, text="使用率:",
                  foreground="#888888",
                  font=("Microsoft YaHei UI", 8)).pack(side=tk.LEFT, padx=(0, 6))
        self._disk_bar = ttk.Progressbar(bar_row, length=400, mode="determinate")
        self._disk_bar.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self._disk_pct_lbl = ttk.Label(
            bar_row, text="0%", width=6,
            font=("Microsoft YaHei UI", 9, "bold"),
        )
        self._disk_pct_lbl.pack(side=tk.LEFT, padx=(8, 0))

        ttk.Button(bar_row, text="刷新", width=6,
                   command=self._refresh_disk_info).pack(side=tk.RIGHT)

    # category list ---------------------------------------------------------

    def _build_category_list(self, parent: ttk.Frame) -> None:
        frame = ttk.LabelFrame(parent, text="清理项目  （仅可清理项可选）", padding="6")
        frame.pack(fill=tk.BOTH, expand=True, pady=(0, 8))

        # toolbar
        tb = ttk.Frame(frame)
        tb.pack(fill=tk.X, pady=(0, 4))

        self._all_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(
            tb, text="全选 / 全不选",
            variable=self._all_var,
            command=self._toggle_all,
        ).pack(side=tk.LEFT)

        self._total_lbl = ttk.Label(
            tb, text="可清理: 0 B",
            font=("Microsoft YaHei UI", 10, "bold"),
            foreground=ACCENT,
        )
        self._total_lbl.pack(side=tk.RIGHT, padx=6)

        # treeview
        cols = ("size", "files", "desc")
        self._tree = ttk.Treeview(
            frame, columns=cols,
            show="tree headings",
            height=12,
            selectmode="browse",
        )
        self._tree.heading("#0",     text="清理项目",   anchor="w")
        self._tree.heading("size",   text="大小",       anchor="center")
        self._tree.heading("files",  text="文件数",     anchor="center")
        self._tree.heading("desc",   text="说明",       anchor="w")

        self._tree.column("#0",    width=260, minwidth=220, stretch=False)
        self._tree.column("size",  width=110, anchor="center", stretch=False)
        self._tree.column("files", width=95,  anchor="center", stretch=False)
        self._tree.column("desc",  width=500, anchor="w")

        vsb = ttk.Scrollbar(frame, orient=tk.VERTICAL, command=self._tree.yview)
        self._tree.configure(yscrollcommand=vsb.set)
        self._tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        vsb.pack(side=tk.RIGHT, fill=tk.Y)

        self._tree.bind("<ButtonRelease-1>", self._on_tree_click)

        # placeholder row
        self._tree.insert("", "end", iid="_placeholder",
                          text='   请先点击"开始扫描"...',
                          values=("", "", ""))

    # buttons ---------------------------------------------------------------

    def _build_buttons(self, parent: ttk.Frame) -> None:
        frame = ttk.Frame(parent)
        frame.pack(fill=tk.X, pady=(0, 8))

        self._scan_btn = ttk.Button(
            frame, text="🔍  开始扫描",
            command=self._on_scan,
            style="Accent.TButton",
        )
        self._scan_btn.pack(side=tk.LEFT, padx=(0, 8))

        self._clean_btn = ttk.Button(
            frame, text="🗑  清理选中",
            command=self._on_clean,
            style="Danger.TButton",
            state=tk.DISABLED,
        )
        self._clean_btn.pack(side=tk.LEFT)

        self._status_lbl = ttk.Label(
            frame,
            text='就绪，点击"开始扫描"检测可清理内容',
            foreground="#666666",
            font=("Microsoft YaHei UI", 9),
        )
        self._status_lbl.pack(side=tk.LEFT, padx=15)

    # progress bar ----------------------------------------------------------

    def _build_progress(self, parent: ttk.Frame) -> None:
        frame = ttk.Frame(parent)
        frame.pack(fill=tk.X, pady=(0, 6))

        self._prog_bar = ttk.Progressbar(frame, mode="determinate")
        self._prog_bar.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 6))

        self._prog_lbl = ttk.Label(
            frame, text="0%", width=7,
            font=("Microsoft YaHei UI", 9),
        )
        self._prog_lbl.pack(side=tk.LEFT)

    # log -------------------------------------------------------------------

    def _build_log(self, parent: ttk.Frame) -> None:
        frame = ttk.LabelFrame(parent, text="操作日志", padding="5")
        frame.pack(fill=tk.X)

        self._log = scrolledtext.ScrolledText(
            frame, height=5,
            state=tk.DISABLED,
            font=("Consolas", 9),
            bg="#1e1e1e", fg="#d4d4d4",
            insertbackground="white",
            relief=tk.FLAT,
        )
        self._log.pack(fill=tk.X)
        self._log.tag_config("ok",    foreground="#4ec9b0")
        self._log.tag_config("skip",  foreground="#ce9178")
        self._log.tag_config("info",  foreground="#9cdcfe")
        self._log.tag_config("error", foreground="#f48771")
        self._log.tag_config("warn",  foreground="#dcdcaa")

    # ------------------------------------------------------------------
    # Disk info
    # ------------------------------------------------------------------

    def _refresh_disk_info(self) -> None:
        total, used, free = get_disk_usage("C:\\")
        if total == 0:
            return
        pct = int(used / total * 100)
        self._disk_labels["total"].config(text=format_bytes(total))
        self._disk_labels["used"].config(text=format_bytes(used))
        self._disk_labels["free"].config(text=format_bytes(free))
        self._disk_bar["value"] = pct
        color = DANGER if pct > 90 else WARNING if pct > 75 else SUCCESS
        self._disk_pct_lbl.config(text=f"{pct}%", foreground=color)

    # ------------------------------------------------------------------
    # Tree interactions
    # ------------------------------------------------------------------

    def _populate_tree(self) -> None:
        self._tree.delete(*self._tree.get_children())
        for cat in self.cleaner.categories:
            if cat.enabled:
                checked = self._checked.get(cat.id, True)
                sym = CHECKED if checked else UNCHECKED
                tag = "row_on" if checked else "row_off"
                name = cat.name
            else:
                sym = "-"
                tag = "row_analysis"
                name = f"{cat.name}（仅分析）"
            self._tree.insert(
                "", "end", iid=cat.id,
                text=f"  {sym}  {name}",
                values=(
                    cat.size_str(),
                    f"{cat.file_count:,}" if cat.file_count else "—",
                    cat.description,
                ),
                tags=(tag,),
            )
        self._tree.tag_configure("row_on",  foreground="#000000")
        self._tree.tag_configure("row_off", foreground="#aaaaaa")
        self._tree.tag_configure("row_analysis", foreground="#777777")
        self._update_total_label()

    def _on_tree_click(self, event: tk.Event) -> None:
        row = self._tree.identify_row(event.y)
        if not row or row == "_placeholder":
            return
        cat = self._cat_by_id(row)
        if cat is None or not cat.enabled:
            return
        self._checked[row] = not self._checked.get(row, True)
        checked = self._checked[row]
        sym = CHECKED if checked else UNCHECKED
        tag = "row_on" if checked else "row_off"
        name = self._cat_name(row)
        self._tree.item(row,
                        text=f"  {sym}  {name}",
                        tags=(tag,))
        self._update_total_label()

    def _cat_name(self, cat_id: str) -> str:
        cat = self._cat_by_id(cat_id)
        if cat is not None:
            return cat.name if cat.enabled else f"{cat.name}（仅分析）"
        return cat_id

    def _cat_by_id(self, cat_id: str):
        for cat in self.cleaner.categories:
            if cat.id == cat_id:
                return cat
        return None

    def _toggle_all(self) -> None:
        state = self._all_var.get()
        for cat in self.cleaner.categories:
            if cat.enabled:
                self._checked[cat.id] = state
        self._populate_tree()

    def _update_total_label(self) -> None:
        total = sum(
            cat.total_size
            for cat in self.cleaner.categories
            if self._checked.get(cat.id, True) and cat.enabled
        )
        self._total_lbl.config(text=f"可清理: {format_bytes(total)}")

    # ------------------------------------------------------------------
    # Log helpers
    # ------------------------------------------------------------------

    def _log_append(self, msg: str, tag: str = "info") -> None:
        self._log.config(state=tk.NORMAL)
        self._log.insert(tk.END, msg + "\n", tag)
        self._log.see(tk.END)
        self._log.config(state=tk.DISABLED)

    def _log_clear(self) -> None:
        self._log.config(state=tk.NORMAL)
        self._log.delete("1.0", tk.END)
        self._log.config(state=tk.DISABLED)

    # ------------------------------------------------------------------
    # Progress helper
    # ------------------------------------------------------------------

    def _set_progress(self, value: float, status: str = "") -> None:
        pct = int(value * 100)
        self._prog_bar["value"] = pct
        self._prog_lbl.config(text=f"{pct}%")
        if status:
            self._status_lbl.config(text=status)

    # ------------------------------------------------------------------
    # Scan
    # ------------------------------------------------------------------

    def _on_scan(self) -> None:
        if self._scanning or self._cleaning:
            return
        self._scanning = True
        self._scan_btn.config(state=tk.DISABLED)
        self._clean_btn.config(state=tk.DISABLED)
        self._log_clear()
        self._checked = {}
        self._log_append("开始扫描磁盘...", "info")
        threading.Thread(target=self._scan_worker, daemon=True).start()

    def _scan_worker(self) -> None:
        def on_progress(value: float, status: str) -> None:
            self.root.after(0, self._set_progress, value, status)
            self.root.after(0, self._log_append, f"  {status}", "info")

        try:
            self.cleaner.scan(on_progress=on_progress)
            for cat in self.cleaner.categories:
                self._checked[cat.id] = cat.enabled
        except Exception as exc:
            self.root.after(0, self._log_append, f"扫描出错: {exc}", "error")
        finally:
            self.root.after(0, self._on_scan_done)

    def _on_scan_done(self) -> None:
        self._scanning = False
        self._scan_btn.config(state=tk.NORMAL)
        self._populate_tree()

        total = sum(c.total_size for c in self.cleaner.categories)
        cleanable_total = sum(
            c.total_size for c in self.cleaner.categories if c.enabled
        )
        if cleanable_total > 0:
            self._clean_btn.config(state=tk.NORMAL)
            self._log_append(
                f"✓ 扫描完成，共找到可清理空间: {format_bytes(cleanable_total)}", "ok"
            )
        else:
            if total > 0:
                self._log_append(
                    "扫描完成，找到系统占用项，但它们仅供分析，不直接清理。", "info"
                )
            else:
                self._log_append("扫描完成，未找到可清理内容。", "info")

        self._refresh_disk_info()

    # ------------------------------------------------------------------
    # Clean
    # ------------------------------------------------------------------

    def _on_clean(self) -> None:
        if self._scanning or self._cleaning:
            return

        selected_ids: List[str] = [
            cat.id
            for cat in self.cleaner.categories
            if self._checked.get(cat.id, True) and cat.total_size > 0 and cat.enabled
        ]
        if not selected_ids:
            messagebox.showinfo("提示", "没有选中任何可清理项目。")
            return

        total_size = sum(
            cat.total_size for cat in self.cleaner.categories
            if cat.id in selected_ids
        )

        if not messagebox.askyesno(
            "确认清理",
            f"即将清理 {len(selected_ids)} 个类别，\n"
            f"预计释放 {format_bytes(total_size)} 空间。\n\n"
            "此操作不可撤销，是否继续？",
        ):
            return

        self._cleaning = True
        self._scan_btn.config(state=tk.DISABLED)
        self._clean_btn.config(state=tk.DISABLED)
        self._log_append("开始清理...", "info")
        threading.Thread(
            target=self._clean_worker,
            args=(selected_ids,),
            daemon=True,
        ).start()

    def _clean_worker(self, selected_ids: List[str]) -> None:
        def on_progress(value: float, status: str) -> None:
            self.root.after(0, self._set_progress, value, status)

        def on_log(msg: str) -> None:
            if msg.startswith("[OK]"):
                tag = "ok"
            elif msg.startswith("[跳过]"):
                tag = "skip"
            elif msg.startswith("[错误]") or msg.startswith("[权限]"):
                tag = "error"
            else:
                tag = "info"
            self.root.after(0, self._log_append, msg, tag)

        try:
            freed, files = self.cleaner.clean(
                selected_ids, on_progress=on_progress, on_log=on_log
            )
            self.root.after(0, self._on_clean_done, freed, files)
        except Exception as exc:
            self.root.after(0, self._log_append, f"清理出错: {exc}", "error")
            self.root.after(0, self._on_clean_done, 0, 0)

    def _on_clean_done(self, freed: int, files: int) -> None:
        self._cleaning = False
        self._log_append(
            f"✓ 清理完成！释放空间: {format_bytes(freed)}，"
            f"删除文件: {files:,} 个",
            "ok",
        )
        self._refresh_disk_info()
        # Automatically re-scan to update sizes
        self._on_scan()

