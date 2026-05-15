# C-PurgeTools

C-PurgeTools 是一个面向 Windows 的 C 盘清理与空间分析工具，使用 Python + Tkinter 编写，提供图形界面、管理员模式启动、常见缓存清理和系统占用分析。

> Author: xiaojie

## 功能

- 扫描 C 盘总容量、已用空间、可用空间和使用率
- 清理用户临时文件、Windows 临时文件、Windows 更新缓存、传递优化缓存
- 清理回收站、浏览器缓存、缩略图缓存、Windows 日志、错误报告、崩溃转储
- 支持通过关闭休眠释放 `C:\hiberfil.sys`
- 分析但不直接删除高风险系统项，例如 `C:\Windows\WinSxS`、`C:\pagefile.sys`、`C:\swapfile.sys`
- EXE 和源码启动脚本都会请求管理员权限

## 直接运行

已打包版本位于：

```text
dist\C盘清理工具.exe
```

双击运行即可。程序会请求管理员权限，这是清理系统目录所必需的。

## 源码运行

```text
run.bat
```

双击 `run.bat` 会自动请求管理员权限并启动源码版本。

## 重新打包

项目内保留了打包脚本：

```text
build_exe.bat
```

打包依赖 PyInstaller。如果本地已有 `.venv-build`，双击脚本即可重新生成：

```text
dist\C盘清理工具.exe
```

## 清理与分析项目

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

## 安全说明

本工具默认以管理员模式运行，但不会直接删除 Windows 核心组件目录。`WinSxS`、页面文件、交换文件等高风险项目只会显示占用信息，不会进入清理队列。

清理操作不可撤销，请在执行前确认勾选项目。

## 文档

- [使用说明](docs/使用说明.md)
- [开发文档](docs/开发文档.md)
- [详细功能说明](docs/README.md)

## 环境

- Windows 10 / Windows 11
- Python 3.8+
- 标准库 Tkinter
- PyInstaller 仅用于打包

## License

MIT License
