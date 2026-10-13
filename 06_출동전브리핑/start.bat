@echo off
chcp 65001 >nul
set PYTHONIOENCODING=utf-8
cd /d "%~dp0projectackend"
python build.py || (pause & exit /b 1)
start "" "%~dp0project\outputriefing.html"
