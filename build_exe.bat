@echo off
setlocal
chcp 65001 >nul

set "ROOT=%~dp0"
set "PY=%ROOT%.venv-build\Scripts\python.exe"
set "PY_HOME=C:\Users\admins\AppData\Local\Programs\Python\Python312"
set "TCL_LIBRARY=%PY_HOME%\tcl\tcl8.6"
set "TK_LIBRARY=%PY_HOME%\tcl\tk8.6"

if not exist "%PY%" (
    echo Build venv not found. Create it first:
    echo   %PY_HOME%\python.exe -m venv .venv-build
    echo   .venv-build\Scripts\python.exe -m pip install pyinstaller
    pause
    exit /b 1
)

"%PY%" -m PyInstaller ^
  --noconfirm ^
  --clean ^
  --onefile ^
  --windowed ^
  --uac-admin ^
  --name "C盘清理工具" ^
  "%ROOT%main.py"

if errorlevel 1 (
    echo.
    echo Build failed.
    pause
    exit /b 1
)

echo.
echo Build complete: %ROOT%dist\C盘清理工具.exe
pause
