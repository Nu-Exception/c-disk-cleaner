@echo off
title Build Disk Cleaner GUI
cd /d "%~dp0"

echo Checking Python...
python --version
if errorlevel 1 (
    echo Python not found. Please install Python first.
    pause
    exit /b
)

echo.
echo Installing / checking PyInstaller...
python -m pip install pyinstaller

echo.
echo Building EXE with icon...
python -m PyInstaller --onefile --clean --noconsole --icon="cs_logo.ico" --name="_v4" "disk_cleaner_v4_gui.py"

echo.
echo Build finished.
echo EXE path:
echo dist\_v4.exe
pause
