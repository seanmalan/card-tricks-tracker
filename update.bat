@echo off
REM Card Shark - one-shot update script for Windows.
REM Pulls the latest code, rebuilds the Docker image, and restarts the app.
setlocal
cd /d "%~dp0"

echo Pulling latest code from GitHub...
git pull
if errorlevel 1 goto :error

echo Stopping running container...
docker compose down
if errorlevel 1 goto :error

echo Rebuilding image and starting...
docker compose up -d --build
if errorlevel 1 goto :error

echo.
echo Done. Open http://localhost:5757 in your browser.
pause
exit /b 0

:error
echo.
echo Update failed. See message above.
pause
exit /b 1
