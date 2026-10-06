@echo off
REM Тест: запуск с VFS и стартовым скриптом (скрипт с ошибкой).
cd /d "%~dp0.."
python -m src.main --vfs "%~dp0..\vfs" --script "%~dp0errors.txt"
pause