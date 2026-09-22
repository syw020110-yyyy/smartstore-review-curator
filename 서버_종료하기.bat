@echo off
chcp 65001 > nul
title LOCAL PROTECTOR 서버 종료기
cd /d "%~dp0"

echo ================================================================
echo   🛑 LOCAL PROTECTOR 8000번 포트 서버 종료 중...
echo ================================================================

for /f "tokens=5" %%a in ('netstat -aon ^| findstr :8000 ^| findstr LISTENING') do (
    taskkill /f /pid %%a > nul 2>&1
)

echo.
echo   ✅ 8000번 포트 서버가 안전하게 종료되었습니다.
echo.
timeout /t 3 > nul
exit
