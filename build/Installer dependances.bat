@echo off
cd /d "%~dp0.."
echo Installation des dependances Diablo Translator...
py -3 build\install_dependencies.py
pause
