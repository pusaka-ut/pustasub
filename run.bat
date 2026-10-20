@echo off
cd /d "%~dp0"
set PYTHON_CMD=python
if exist python\python.exe set PYTHON_CMD=python\python.exe

for /f "tokens=5" %%a in ('netstat -aon ^| findstr :8765 ^| findstr LISTENING') do (
    taskkill /F /PID %%a >nul 2>&1
)

start "" cmd /c "timeout /t 2 /nobreak >nul && start http://127.0.0.1:8765/admin"
%PYTHON_CMD% -m uvicorn engine.server:app --host 127.0.0.1 --port 8765 --log-level info
pause
