@echo off
REM Тест: запуск со стартовым скриптом.
cd /d "%~dp0.."
python -m src.main --script "%~dp0demo.txt"
pause