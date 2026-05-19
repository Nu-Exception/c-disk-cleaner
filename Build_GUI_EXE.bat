@echo off
title Build Disk Cleaner v4.2 GUI
cd /d "%~dp0"
echo Checking PyInstaller...
python -m pip install pyinstaller
echo.
echo Building GUI EXE...
python -m PyInstaller --onefile --clean --noconsole --icon="cs_logo.ico" --name="_v4.2_GUI" "disk_cleaner_v4_gui.py"
echo.
echo Done. EXE path: dist\_v4.2_GUI.exe
pause
