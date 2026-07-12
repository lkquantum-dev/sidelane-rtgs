@echo off
REM SideLane-RTGS - Windows 一键环境准备与启动器(双击本文件即可)
setlocal
cd /d "%~dp0"
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0setup-windows.ps1"
echo.
pause
