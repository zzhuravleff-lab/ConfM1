@echo off
REM Тест: минимальный VFS (одна папка).
cd /d "%~dp0.."
python -m src.main --vfs "%~dp0..\vfs\minimal.xml"
pause