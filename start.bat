@echo off
echo Starting CET-6 Vocabulary App...

echo Starting backend server...
start "Backend" cmd /k "cd /d %~dp0backend && python main.py"

timeout /t 3 /nobreak >nul

echo Starting frontend server...
start "Frontend" cmd /k "cd /d %~dp0backend\frontend && npm run dev"

echo.
echo Backend: http://localhost:8000
echo Frontend: http://localhost:5173
echo.
echo Press any key to exit...
pause >nul
