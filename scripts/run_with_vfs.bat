@echo off
REM Тест: запуск с указанием VFS.
python "%~dp0..\src\main.py" --vfs "%~dp0..\vfs"
pause