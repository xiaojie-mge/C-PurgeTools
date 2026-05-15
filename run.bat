@echo off
setlocal
chcp 65001 >nul

net session >nul 2>&1
if %errorlevel%==0 (
    if exist "C:\Users\admins\AppData\Local\Programs\Python\Python312\python.exe" (
        "C:\Users\admins\AppData\Local\Programs\Python\Python312\python.exe" "%~dp0main.py"
        exit /b %errorlevel%
    )
    where py >nul 2>nul
    if not errorlevel 1 (
        py -3 "%~dp0main.py"
        exit /b %errorlevel%
    )
    echo Python 3.8+ not found. Please install Python and try again.
    pause
    exit /b 1
) else (
    powershell -NoProfile -Command "Start-Process cmd -Verb RunAs -ArgumentList '/c ""%~f0""'"
)
