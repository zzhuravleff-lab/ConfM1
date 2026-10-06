@echo off
REM Тест: запуск с VFS и стартовым скриптом (скрипт с ошибкой).
python "%~dp0..\src\main.py" --vfs "%~dp0..\vfs" --script "%~dp0errors.txt"
pause