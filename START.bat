@echo off
REM Diablo Translator v2 — UN SEUL LANCEUR
REM   START.bat         Interface traduction (defaut)
REM   START.bat hub     Sanctuaire (menu avance)
REM   START.bat build   Construire DiabloTranslator.exe
REM   START.bat web     Companion web (API + Next.js)
setlocal
cd /d "%~dp0"
set "PY=%~dp0..\.venv\Scripts\python.exe"
if not exist "%PY%" set "PY=py -3"
if not exist "%PY%" set "PY=python"
if not defined DT_NODE_HOME if exist "C:\src\node.exe" set "DT_NODE_HOME=C:\src"

set "MODE=%~1"
if "%MODE%"=="" goto gui
if /I "%MODE%"=="gui" goto gui
if /I "%MODE%"=="hub" goto hub
if /I "%MODE%"=="menu" goto hub
if /I "%MODE%"=="build" goto build
if /I "%MODE%"=="web" goto web
goto gui

:gui
"%PY%" launcher.py gui
goto end

:hub
"%PY%" launcher.py menu
goto end

:build
call build\Build-Pro.bat
goto end

:web
start "Diablo API" cmd /k "%PY%" launcher.py server
timeout /t 3 /nobreak >nul
"%PY%" launcher.py web
goto end

:end
if errorlevel 1 pause
exit /b %ERRORLEVEL%
