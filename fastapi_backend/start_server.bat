@echo off
REM FastAPI ML Analytics Backend Startup Script for Windows

echo 🚀 Starting FastAPI ML Analytics Backend...

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python is not installed or not in PATH
    pause
    exit /b 1
)

REM Check if pip is installed
pip --version >nul 2>&1
if errorlevel 1 (
    echo ❌ pip is not installed or not in PATH
    pause
    exit /b 1
)

REM Create virtual environment if it doesn't exist
if not exist "venv" (
    echo 📦 Creating virtual environment...
    python -m venv venv
)

REM Activate virtual environment
echo 🔧 Activating virtual environment...
call venv\Scripts\activate.bat

REM Install requirements
echo 📥 Installing requirements...
pip install -r requirements.txt

REM Create uploads directory
echo 📁 Creating uploads directory...
if not exist "uploads" mkdir uploads

REM Start FastAPI server
echo 🌟 Starting FastAPI server...
echo 📖 API Documentation: http://localhost:8000/docs
echo 🔍 Alternative Docs: http://localhost:8000/redoc
echo 🏠 API Root: http://localhost:8000
echo.
echo Press Ctrl+C to stop the server

uvicorn main:app --host 0.0.0.0 --port 8000 --reload



