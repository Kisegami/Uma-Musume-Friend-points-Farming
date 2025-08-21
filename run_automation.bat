@echo off
echo Starting Uma Friend Point Farm Automation...
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python is not installed or not in PATH
    echo Please install Python 3.7+ and add it to your system PATH
    pause
    exit /b 1
)

REM Check if requirements are installed
echo Checking Python dependencies...
pip show opencv-python >nul 2>&1
if errorlevel 1 (
    echo Installing Python dependencies...
    pip install -r requirements.txt
    if errorlevel 1 (
        echo Error: Failed to install dependencies
        pause
        exit /b 1
    )
)

REM Test setup first
echo Testing setup...
python test_setup.py
if errorlevel 1 (
    echo Setup test failed. Please fix the issues above.
    pause
    exit /b 1
)

echo.
echo Setup test passed! Starting automation...
echo Press Ctrl+C to stop the automation when needed.
echo.

REM Run the automation
python uma_automation.py

echo.
echo Automation stopped.
pause
