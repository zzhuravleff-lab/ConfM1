@echo off
REM Этап 5: полный тест touch и rmdir.

cd /d "%~dp0.."

echo === Test 1: touch and rmdir (success) ===
python -m src.main --vfs "vfs\stage5.xml" --script "scripts\stage5_ok.txt"

echo.
echo === Test 2: touch error (directory) ===
python -m src.main --vfs "vfs\stage5.xml" --script "scripts\stage5_err_touch.txt"

echo.
echo === Test 3: rmdir error (not empty) ===
python -m src.main --vfs "vfs\stage5.xml" --script "scripts\stage5_err_rmdir.txt"

pause