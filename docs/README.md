# C-PurgeTools 功能说明

> 一款 Windows C 盘清理与空间分析工具，基于 Python + Tkinter，无需第三方运行时依赖。

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
| Firefox 缓存 | Mozilla Firefox cache2 缓存 |
| 缩略图缓存 | Windows 资源管理器缩略图数据库文件 |
| Windows 日志 | `C:\Windows\Logs` 系统日志文件 |
| 预读取缓存 | Windows Prefetch 文件 |
| 错误报告存档 | Windows 错误报告存档与队列文件 |
| 传递优化缓存 | Windows Update 传递优化下载缓存 |
| 休眠文件 | `C:\hiberfil.sys`，通过关闭休眠释放空间 |
| 页面文件 | `C:\pagefile.sys` / `C:\swapfile.sys`，仅分析 |
| 内存转储 | `C:\Windows\MEMORY.DMP` 崩溃转储文件 |
| 小型转储 | `C:\Windows\Minidump` 崩溃转储目录 |
| WinSxS 组件存储 | 系统组件存储，仅分析，不直接删除 |

## 运行方式

- EXE: `dist\C盘清理工具.exe`
- 源码: `run.bat`
- 打包: `build_exe.bat`

## 项目结构

```text
C-PurgeTools/
├── src/c_purge_tools/   # 应用源码
├── scripts/             # 辅助脚本
├── docs/                # 文档
├── dist/                # 打包产物
├── main.py              # 源码兼容启动器
├── run.bat              # 管理员源码启动器
└── C-PurgeTools.spec    # PyInstaller 配置
```

## 注意事项

- 本工具面向 C 盘系统清理，默认以管理员模式运行。
- 清理预读取缓存后，部分程序首次启动速度会暂时变慢。
- WinSxS 组件存储和页面文件只做分析，不会直接删除。
- 清理休眠文件会通过关闭休眠实现，并同时关闭快速启动。
- 清理操作不可撤销。

## 许可证

MIT License
