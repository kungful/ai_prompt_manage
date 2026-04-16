@echo off
chcp 65001 >nul
echo ================================
echo   Prompt Manager Build Script
echo ================================

pip show pyinstaller >nul 2>&1
if errorlevel 1 (
    echo Installing PyInstaller...
    pip install pyinstaller
)

echo Cleaning old build...
if exist "dist" rmdir /s /q "dist"
if exist "build" rmdir /s /q "build"

echo Building...
pyinstaller main.spec

if errorlevel 1 (
    echo Build failed!
    pause
    exit /b 1
)

echo ================================
echo Build complete!
echo Output: dist\PromptManager\PromptManager.exe
echo ================================
pause