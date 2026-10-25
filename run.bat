@echo off
setlocal
title Wayfare Launcher
cd /d "%~dp0"

echo ============================================
echo   Wayfare - Personalized Travel Itinerary Planner
echo ============================================
echo.

where python >nul 2>nul
if errorlevel 1 (
  echo [ERROR] Python 3.10 or newer was not found. Install it from https://www.python.org and tick "Add to PATH".
  pause
  exit /b 1
)
where node >nul 2>nul
if errorlevel 1 (
  echo [ERROR] Node.js 18 or newer was not found. Install it from https://nodejs.org
  pause
  exit /b 1
)

REM ---- Backend setup ----
if not exist "backend\.env" (
  echo Creating backend\.env from the example file...
  copy "backend\.env.example" "backend\.env" >nul
)
if not exist "backend\venv\Scripts\python.exe" (
  echo Creating Python virtual environment...
  python -m venv backend\venv
  if errorlevel 1 (
    echo [ERROR] Could not create the virtual environment.
    pause
    exit /b 1
  )
)
echo Installing backend dependencies...
"backend\venv\Scripts\python.exe" -m pip install --disable-pip-version-check -q -r backend\requirements.txt
if errorlevel 1 (
  echo [ERROR] Backend dependency install failed. Check your internet connection.
  pause
  exit /b 1
)

REM ---- Frontend setup ----
if not exist "frontend\node_modules" (
  echo Installing frontend dependencies, this can take a minute...
  pushd frontend
  call npm install
  if errorlevel 1 (
    popd
    echo [ERROR] npm install failed. Check your internet connection.
    pause
    exit /b 1
  )
  popd
)

REM ---- Launch ----
echo Starting the API on http://localhost:8000 ...
start "Wayfare API" cmd /k "cd /d %~dp0backend && venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload"

echo Starting the web app on http://localhost:5173 ...
start "Wayfare UI" cmd /k "cd /d %~dp0frontend && npm run dev"

echo Waiting for the servers to come up...
timeout /t 8 /nobreak >nul
start "" http://localhost:5173

echo.
echo Both servers are running in their own windows. Close those windows to stop the app.
echo API docs: http://localhost:8000/docs
echo.
pause
endlocal
