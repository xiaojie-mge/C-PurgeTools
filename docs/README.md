# C盘清理工具

> 一款轻量级的 Windows C 盘垃圾文件清理工具，基于 Python + Tkinter，无需安装任何第三方依赖。

---

## 功能特性

| 清理类别 | 说明 |
|---|---|
| 用户临时文件 | `%TEMP%` 目录中的残留临时文件 |
| Windows 临时文件 | `C:\Windows\Temp` 系统临时目录 |
| Windows 更新缓存 | Update 下载缓存（已安装更新不受影响） |
| Windows.old | 系统升级遗留的旧系统目录 |
| 回收站 | 所有驱动器回收站中已删除的文件 |
| Chrome 缓存 | Google Chrome 浏览器缓存与代码缓存 |
| Edge 缓存 | Microsoft Edge 浏览器缓存与代码缓存 |
| Firefox 缓存 | Mozilla Firefox 浏览器 cache2 缓存 |
| 缩略图缓存 | Windows 资源管理器缩略图数据库文件 |
| Windows 日志 | `C:\Windows\Logs` 系统日志文件 |
| 预读取缓存 | Windows Prefetch 文件 |
| 错误报告存档 | Windows 错误报告存档与队列文件 |
| 传递优化缓存 | Windows Update 传递优化下载缓存 |
| 休眠文件 | `C:\hiberfil.sys`，可通过关闭休眠释放空间 |
| 页面文件 | `C:\pagefile.sys` / `C:\swapfile.sys`，仅分析 |
| 内存转储 | `C:\Windows\MEMORY.DMP` 崩溃转储文件 |
| 小型转储 | `C:\Windows\Minidump` 崩溃转储目录 |
| WinSxS 组件存储 | 系统组件存储，仅分析，不直接删除 |

## 运行环境

- **操作系统**：Windows 10 / Windows 11
- **Python**：3.8 或更高版本
- **依赖**：仅使用 Python 标准库（`tkinter`、`os`、`shutil`、`ctypes`、`threading`）

## 快速开始

### EXE 版本

双击 `dist\C盘清理工具.exe`。该程序会自动请求管理员权限。

### 源码运行

双击 `run.bat`。该脚本会自动请求管理员权限后启动源码版本。

## 目录结构

```
C-PurgeTools/
├── main.py          # 程序入口
├── gui.py           # 图形界面
├── cleaner.py       # 核心扫描与清理逻辑
├── config.py        # 配置管理
├── config.json      # 用户配置（运行后自动生成）
├── requirements.txt # 依赖说明
├── run.bat          # 管理员模式启动脚本
├── run_admin.bat    # 兼容保留的管理员模式启动脚本
├── build_exe.bat    # EXE 打包脚本
└── docs/            # 文档目录
    ├── README.md        # 本文件
    ├── 使用说明.md      # 详细使用指南
    └── 开发文档.md      # 开发者文档
```

## 使用截图说明

程序启动后界面分为四个区域：

1. **顶部标题栏** — 显示程序名称及当前权限状态（普通用户 / 管理员）
2. **磁盘信息** — 实时显示 C 盘总容量、已用空间、可用空间及使用率
3. **清理项目列表** — 勾选/取消勾选各清理类别，显示每类大小与文件数
4. **操作日志** — 实时滚动展示扫描和清理过程的详细日志

## 注意事项

- 本工具面向 C 盘系统清理，默认以管理员模式运行。
- 清理 **预读取缓存** 后，部分程序首次启动速度会暂时变慢，属正常现象。
- **WinSxS 组件存储** 和 **页面文件** 只做分析，不会直接删除。
- 清理 **休眠文件** 会通过关闭休眠实现，并同时关闭快速启动。
- 清理操作**不可撤销**，执行前请确认无误。
- 本工具只清理目录内容，不删除目录本身，不影响 Windows 正常运行。

## 许可证

MIT License

