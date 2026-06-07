@echo off
cd /d "%~dp0.."
echo ============================================================
echo  DIABLO TRANSLATOR - BUILD PRO
echo  Controles + DLL + manifest Windows + securite MOTW
echo ============================================================
echo.
py -3 build\build.py --pro
if errorlevel 1 (
    echo.
    echo Build echoue. Fermez DiabloTranslator.exe puis relancez.
    pause
    exit /b 1
)
echo.
echo Termine. Lancez : build\launch_app.ps1
pause
