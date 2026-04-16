@echo off
echo Starting Prompt Manager...
python main.py
if errorlevel 1 (
    echo Error: Failed to start application
    pause
    exit /b 1
)