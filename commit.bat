@echo off
chcp 65001 > nul
python "%~dp0commit.py" %*
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo 执行过程中出现提示或错误。
)
if "%1"=="" (
    pause
)
