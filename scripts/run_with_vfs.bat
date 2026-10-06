@echo off
REM Тест: запуск с указанием VFS.
cd /d "%~dp0.."
python -m src.main --vfs "%~dp0..\vfs"
pause