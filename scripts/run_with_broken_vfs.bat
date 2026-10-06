@echo off
REM Тест: VFS с битым XML (ошибка парсинга).
cd /d "%~dp0.."
python -m src.main --vfs "%~dp0..\vfs\broken.xml"
pause