@echo off
REM Тест Этапа 4: полный прогон всех команд.
cd /d "%~dp0.."
python -m src.main --vfs "vfs\multi.xml" --script "scripts\startup_stage4.txt"
pause