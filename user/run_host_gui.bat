@echo off
setlocal enabledelayedexpansion
title Lucky48 Host System Launcher

:: Change directory to the script's root folder
cd /d "%~dp0"

echo ========================================================
echo               Lucky48 Host System Launcher              
echo ========================================================
echo.

:: 1. Check if app_gui.py exists
if not exist "app_gui.py" (
    color 0C
    echo [ERROR] Core entry point 'app_gui.py' was not found in this directory.
    echo Please ensure the script is placed inside the root project directory.
    echo.
    pause
    exit /b 1
)

:: 2. Detect Python Environment (VirtualEnv or System Python)
set "PYTHON_BIN=python"

if exist "venv\Scripts\python.exe" (
    set "PYTHON_BIN=venv\Scripts\python.exe"
    echo [INFO] Virtual environment detected: venv
) else if exist ".venv\Scripts\python.exe" (
    set "PYTHON_BIN=.venv\Scripts\python.exe"
    echo [INFO] Virtual environment detected: .venv
)

:: 3. Verify Python Executable Availability
%PYTHON_BIN% --version >nul 2>&1
if %ERRORLEVEL% neq 0 (
    color 0C
    echo [ERROR] Python is not installed or not added to system PATH.
    echo Please install Python 3.9+ and make sure to check "Add Python to PATH".
    echo.
    pause
    exit /b 1
)

:: 4. Launch Application
echo [INFO] Launching Lucky48 Host GUI...
echo.

start "" %PYTHON_BIN% app_gui.py

if %ERRORLEVEL% equ 0 (
    echo [SUCCESS] Application launched successfully.
    timeout /t 3 >nul
    exit /b 0
) else (
    color 0C
    echo [ERROR] Failed to execute 'app_gui.py'. Return code: %ERRORLEVEL%
    echo.
    pause
    exit /b %ERRORLEVEL%
)