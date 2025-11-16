@echo off
REM spyTrade Application Startup Script for Windows
REM This script sets up and launches the spyTrade dashboard

setlocal enabledelayedexpansion

echo.
echo ======================================================================
echo                    spyTrade Startup Script
echo ======================================================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python is not installed or not in PATH
    echo Please install Python 3.8 or higher from https://www.python.org/
    pause
    exit /b 1
)

for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
echo [OK] Python %PYTHON_VERSION% detected

REM Check if we're in the right directory
if not exist "requirements.txt" (
    echo Error: requirements.txt not found
    echo Please run this script from the spyTrade directory
    pause
    exit /b 1
)

REM Create virtual environment if it doesn't exist
if not exist "venv" (
    echo.
    echo Creating virtual environment...
    python -m venv venv
    echo [OK] Virtual environment created
)

REM Activate virtual environment
echo.
echo Activating virtual environment...
call venv\Scripts\activate.bat
echo [OK] Virtual environment activated

REM Install/upgrade dependencies
echo.
echo Installing dependencies...
python -m pip install -q --upgrade pip
pip install -q -r requirements.txt
echo [OK] Dependencies installed

REM Check if .env exists
if not exist ".env" (
    echo.
    echo Creating .env file from template...
    copy .env.example .env >nul
    echo [OK] .env file created
    echo.
    echo WARNING: Edit .env and add your API keys (optional, see SETUP.md)
)

REM Start the application
echo.
echo ======================================================================
echo            Starting spyTrade Dashboard...
echo ======================================================================
echo.
echo Dashboard will open in your browser at: http://localhost:5000
echo.
echo Features:
echo   - Real-time price charts
echo   - Technical indicators (RSI, MACD, SMA)
echo   - Trade signals with confidence scores
echo   - News sentiment analysis
echo   - Risk/reward calculations
echo.
echo Press Ctrl+C to stop the server
echo.

python dashboard.py

pause
