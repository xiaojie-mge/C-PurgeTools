# C-PurgeTools

C-PurgeTools 是一个面向 Windows 的 C 盘清理与空间分析工具，使用 Python + Tkinter 编写。项目采用 `src` 包结构，保留源码运行、管理员启动和 PyInstaller 打包能力。

> Author: xiaojie

## Highlights

- Administrator-first: EXE 和脚本都会请求管理员权限
- Clean + Analyze: 可清理项和仅分析项分离，避免误删系统组件
- Windows-focused: 覆盖临时文件、更新缓存、浏览器缓存、日志、崩溃转储等常见占用
- Safer defaults: `WinSxS`、页面文件、交换文件只展示占用，不直接删除
- Portable build: `dist\C盘清理工具.exe` 可直接运行

## Quick Start

### 直接运行 EXE

```text
dist\C盘清理工具.exe
```

### 从源码运行

```text
run.bat
```

### 重新打包

```text
build_exe.bat
```

根目录 `build_exe.bat` 会转发到 `scripts\build_exe.bat`。打包配置使用 `C-PurgeTools.spec`。

## Project Layout

```text
C-PurgeTools/
├── src/
│   └── c_purge_tools/
│       ├── __init__.py
│       ├── app.py          # Tkinter 应用入口
│       ├── cleaner.py      # 扫描与清理核心逻辑
│       ├── config.py       # 配置路径与 JSON 持久化
│       └── gui.py          # GUI 界面与交互
├── scripts/
│   ├── build_exe.bat       # 实际打包脚本
│   └── run_admin.bat       # 兼容入口
├── docs/
│   ├── README.md           # 功能说明
│   ├── 使用说明.md
│   └── 开发文档.md
├── dist/
│   └── C盘清理工具.exe     # 已打包产物
├── main.py                 # 源码兼容启动器
├── run.bat                 # 管理员源码启动器
├── build_exe.bat           # 根目录打包入口
├── C-PurgeTools.spec       # PyInstaller 配置
├── requirements.txt
└── README.md
```

## Cleanable Items

| 项目 | 行为 |
|---|---|
| 用户临时文件 | 可清理 |
| Windows 临时文件 | 可清理 |
| Windows 更新缓存 | 可清理 |
| 传递优化缓存 | 可清理 |
| 回收站 | 可清理 |
| Chrome / Edge / Firefox 缓存 | 可清理 |
| 缩略图缓存 | 可清理 |
| Windows 日志 | 可清理 |
| 错误报告 / 崩溃转储 | 可清理 |
| 休眠文件 | 通过 `powercfg /h off` 释放 |
| WinSxS 组件存储 | 仅分析，不直接删除 |
| 页面文件 / 交换文件 | 仅分析，不直接删除 |

## Safety Notes

本工具默认以管理员模式运行。清理操作不可撤销，请在执行前确认勾选项目。

`WinSxS`、`pagefile.sys`、`swapfile.sys` 等高风险系统项只做分析，不会进入清理队列。

## Docs

- [使用说明](docs/使用说明.md)
- [开发文档](docs/开发文档.md)
- [详细功能说明](docs/README.md)

## Requirements

- Windows 10 / Windows 11
- Python 3.8+
- Tkinter
- PyInstaller only for packaging

## License

MIT License
