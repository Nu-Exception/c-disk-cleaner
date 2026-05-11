@echo off
chcp 65001 >nul
cd /d "%~dp0"
title Disk Cleaner v3
python disk_cleaner_v3.py
pause
