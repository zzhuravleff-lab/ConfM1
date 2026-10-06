@echo off
REM Тест: запуск со скриптом, содержащим кавычки.
cd /d "%~dp0.."
python -m src.main --vfs "%~dp0..\vfs" --script "%~dp0quotes.txt"
pause