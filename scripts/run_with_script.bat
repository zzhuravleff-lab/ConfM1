@echo off
REM Тест: запуск со стартовым скриптом.
python "%~dp0..\src\main.py" --script "%~dp0demo.txt"
pause