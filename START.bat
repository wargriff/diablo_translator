@echo off
REM Diablo Translator — UN SEUL LANCEUR → Centre de controle
REM   START.bat           Centre de controle (defaut)
REM   START.bat gui       Interface OCR en jeu
REM   START.bat build     Construire DiabloTranslator.exe
setlocal
cd /d "%~dp0"
set "PY=%~dp0..\.venv\Scripts\python.exe"
if not exist "%PY%" set "PY=py -3"
if not exist "%PY%" set "PY=python"
if not defined DT_NODE_HOME if exist "C:\src\node.exe" set "DT_NODE_HOME=C:\src"

set "MODE=%~1"
if "%MODE%"=="" goto control
if /I "%MODE%"=="control" goto control
if /I "%MODE%"=="hub" goto control
if /I "%MODE%"=="menu" goto control
if /I "%MODE%"=="gui" goto gui
if /I "%MODE%"=="build" goto build
if /I "%MODE%"=="web" goto web
goto control

:control
"%PY%" launcher.py control
goto end

:gui
"%PY%" launcher.py gui
goto end

:build
call build\Build-Pro.bat
goto end

:web
"%PY%" launcher.py control
goto end

:end
if errorlevel 1 pause
exit /b %ERRORLEVEL%
