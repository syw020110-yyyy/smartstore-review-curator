@echo off
echo =========================================
echo [1/3] Killing existing server on port 8000...
echo =========================================
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :8000') do (
    taskkill /f /pid %%a > nul 2>&1
)

echo [2/3] Starting Python Server...
cd /d "%~dp0"
start /b python server.py

timeout /t 2 > nul

echo [3/3] Opening Browser...
start http://localhost:8000/index.html

echo =========================================
echo Server is running! DO NOT CLOSE THIS WINDOW.
echo =========================================
pause