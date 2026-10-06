@echo off
REM Тест Этапа 4: интерактивная проверка history.
cd /d "%~dp0.."
python -m src.main --vfs "vfs\multi.xml"
pause