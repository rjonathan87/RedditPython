@echo off
echo Instalando paquetes de procesamiento de video...
powershell -ExecutionPolicy Bypass -File "%~dp0install_video_packages.ps1"
pause
