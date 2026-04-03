@echo off
REM Build a standalone Windows .exe

python -m venv venv
call venv\Scripts\activate.bat
pip install -r requirements.txt
pip install pyinstaller

pyinstaller ^
  --onefile ^
  --windowed ^
  --name "Card Magic Tracker" ^
  --add-data "static;static" ^
  --collect-all pywebview ^
  --collect-all flask ^
  main.py

call venv\Scripts\deactivate.bat
echo.
echo Done! App is at: dist\Card Magic Tracker.exe
pause
