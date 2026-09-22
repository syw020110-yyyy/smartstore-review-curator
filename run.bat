@echo off
chcp 65001 > nul
echo ========================================================
echo  Smartstore Review Curator ^& Insight Extractor
echo ========================================================
echo.
echo 대시보드 서버를 실행 중입니다...
echo 잠시 후 웹 브라우저가 열립니다 (http://localhost:8501)
echo.
if exist "C:\Users\suhye\AppData\Local\Python\pythoncore-3.14-64\python.exe" (
    "C:\Users\suhye\AppData\Local\Python\pythoncore-3.14-64\python.exe" -m streamlit run app.py
) else (
    python -m streamlit run app.py
)
pause
