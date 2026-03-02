@echo off
setlocal
chcp 65001 >nul

echo === Запуск AI Car Damage Detector ===
echo.

IF EXIST "venv\Scripts\activate.bat" (
    echo Активация виртуального окружения (venv)...
    call venv\Scripts\activate.bat
)

echo Остановка старых процессов на портах 8000 и 8501...
for /f "tokens=5" %%a in ('netstat -aon ^| find "8000"') do taskkill /f /pid %%a >nul 2>&1
for /f "tokens=5" %%a in ('netstat -aon ^| find "8501"') do taskkill /f /pid %%a >nul 2>&1

echo Запуск Backend (FastAPI)...
start "FastAPI Backend" cmd /k "python -m uvicorn main:app --reload"

timeout /t 2 /nobreak >nul

echo Запуск Frontend (Streamlit)...
start "Streamlit Frontend" cmd /k "python -m streamlit run streamlit_app.py --server.headless=true"

timeout /t 2 /nobreak >nul
start http://localhost:8501

echo.
echo =====================================
echo Приложение открыто в новых окнах!
echo UI: http://localhost:8501
echo API: http://localhost:8000/docs
echo =====================================
