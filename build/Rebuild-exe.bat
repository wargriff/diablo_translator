@echo off
cd /d "%~dp0.."
py -3 build\build.py --shortcut
if errorlevel 1 (
    echo Build echoue. Fermez DiabloTranslator.exe puis relancez.
    pause
    exit /b 1
)
pause
