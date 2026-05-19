@echo off
title Build Disk Cleaner v4.2 All
cd /d "%~dp0"
echo Checking PyInstaller...
python -m pip install pyinstaller
echo.
echo Building GUI EXE...
python -m PyInstaller --onefile --clean --noconsole --icon="cs_logo.ico" --name="_v4.2_GUI" "disk_cleaner_v4_gui.py"
echo.
echo Building CMD EXE...
python -m PyInstaller --onefile --clean --icon="cs_logo.ico" --name="_v4.2_CMD" "disk_cleaner_v4_cmd.py"
echo.
echo Done.
pause
