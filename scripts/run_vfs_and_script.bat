@echo off
REM Тест: VFS + стартовый скрипт (motd + все команды).
cd /d "%~dp0.."
python -m src.main --vfs "%~dp0..\vfs\multi.xml" --script "%~dp0startup_full.txt"
pause