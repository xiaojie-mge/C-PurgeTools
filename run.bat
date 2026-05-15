@echo off
setlocal
chcp 65001 >nul

net session >nul 2>&1
if %errorlevel%==0 (
    where py >nul 2>nul
    if errorlevel 1 (
        echo Python launcher not found. Please install Python 3.8+ and try again.
        pause
        exit /b 1
    )
    py -3 "%~dp0main.py"
) else (
    powershell -NoProfile -Command "Start-Process cmd -Verb RunAs -ArgumentList '/c ""%~f0""'"
)
