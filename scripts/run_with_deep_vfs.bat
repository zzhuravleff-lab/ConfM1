@echo off
REM Тест: VFS с 3+ уровнями вложенности.
cd /d "%~dp0.."
python -m src.main --vfs "%~dp0..\vfs\deep.xml"
pause