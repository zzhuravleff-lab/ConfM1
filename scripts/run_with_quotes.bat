@echo off
REM Тест: запуск со скриптом, содержащим кавычки.
python "%~dp0..\src\main.py" --vfs "%~dp0..\vfs" --script "%~dp0quotes.txt"
pause