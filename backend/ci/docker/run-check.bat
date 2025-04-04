@echo off
echo 正在检查Docker环境...
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0check-docker-env.ps1"
if %ERRORLEVEL% EQU 0 (
    echo Docker环境检查通过！
) else (
    echo Docker环境检查失败，请查看详细信息。
)
pause 