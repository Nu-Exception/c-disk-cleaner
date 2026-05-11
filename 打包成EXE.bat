@echo off
chcp 65001 >nul
cd /d "%~dp0"
title Disk Cleaner v3 - Build EXE

echo 正在检查 PyInstaller...
python -m pip install --upgrade pip
python -m pip install pyinstaller

echo.
echo 正在打包 DiskCleaner_v3.exe...
pyinstaller --onefile --clean --name DiskCleaner_v3 disk_cleaner_v3.py

echo.
echo 打包完成。
echo 生成位置：dist\DiskCleaner_v3.exe
echo.
pause
