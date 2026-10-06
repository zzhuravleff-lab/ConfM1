@echo off
REM Тест: VFS с motd и несколькими файлами.
cd /d "%~dp0.."
python -m src.main --vfs "%~dp0..\vfs\multi.xml"
pause