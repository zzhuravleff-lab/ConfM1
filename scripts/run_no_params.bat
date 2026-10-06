@echo off
REM Тест: запуск без параметров (интерактивный REPL).
cd /d "%~dp0.."
python -m src.main
pause