@echo off
cd /d "%~dp0.."
echo Verification des modules...
py -3 -c "import src.translation.language_detection_service, src.translation.conversation_context" || (
    echo Erreur : fichiers source manquants. Lancez git pull.
    pause
    exit /b 1
)
echo Build DiabloTranslator.exe...
py -3 build\build.py
if errorlevel 1 (
    echo Build echoue. Fermez DiabloTranslator.exe puis relancez.
    pause
    exit /b 1
)
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0create_desktop_shortcut.ps1"
echo Termine.
pause
