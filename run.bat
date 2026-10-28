@echo off
setlocal
title Tripora Launcher
cd /d "%~dp0"

echo ============================================
echo   Tripora - Personalized Travel Itinerary Planner
echo ============================================
echo.

REM ---- Check Node.js and npm ----
where node >nul 2>nul
if errorlevel 1 (
  echo [ERROR] Node.js was not found. Please install Node.js 18 or newer from https://nodejs.org
  pause
  exit /b 1
)
where npm >nul 2>nul
if errorlevel 1 (
  echo [ERROR] npm was not found. Please verify your Node.js installation.
  pause
  exit /b 1
)

REM ---- Backend setup ----
if not exist "backend\.env" (
  echo Creating backend\.env from the example file...
  copy "backend\.env.example" "backend\.env" >nul
)

if not exist "backend\venv\Scripts\python.exe" (
  echo Locating Python to create virtual environment...
  py -3 --version >nul 2>nul && py -3 -m venv backend\venv
  if not exist "backend\venv\Scripts\python.exe" (
    py --version >nul 2>nul && py -m venv backend\venv
  )
  if not exist "backend\venv\Scripts\python.exe" (
    python --version >nul 2>nul && python -m venv backend\venv
  )
  if not exist "backend\venv\Scripts\python.exe" (
    echo [ERROR] Python 3.10 or newer was not found.
    echo Please install Python from https://www.python.org and tick Add to PATH.
    pause
    exit /b 1
  )
)

REM Check if backend dependencies are already installed
"backend\venv\Scripts\python.exe" -m pip check >nul 2>nul
if errorlevel 1 (
  echo Installing backend dependencies...
  "backend\venv\Scripts\python.exe" -m pip install --disable-pip-version-check --progress-bar off --timeout 20 --retries 1 --only-binary :all: -r backend\requirements.txt
  if errorlevel 1 (
    echo [ERROR] Backend dependency install failed.
    echo Check your internet connection or inspect backend\requirements.txt.
    pause
    exit /b 1
  )
) else (
  echo Backend dependencies are already installed.
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
start "Tripora API" cmd /k "cd /d %~dp0backend && venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload"

echo Starting the web app on http://localhost:5173 ...
start "Tripora UI" cmd /k "cd /d %~dp0frontend && npm run dev"

echo Waiting for the servers to come up...
timeout /t 5 >nul 2>&1 || ping 127.0.0.1 -n 6 >nul
start "" http://localhost:5173

echo.
echo Both servers are running in their own windows. Close those windows to stop the app.
echo API docs: http://localhost:8000/docs
echo.
pause
endlocal
