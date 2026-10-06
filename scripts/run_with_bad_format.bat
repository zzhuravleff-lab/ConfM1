@echo off
REM Тест: VFS с неверным корневым тегом.
cd /d "%~dp0.."
python -m src.main --vfs "%~dp0..\vfs\bad_format.xml"
pause