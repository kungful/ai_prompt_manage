@echo off
echo Converting GUI.ui to Python file...
pyuic6 -x GUI.ui -o ui_main.py
if errorlevel 1 (
    echo Error: Failed to convert UI file
    pause
    exit /b 1
)
echo Success! ui_main.py has been created
pause