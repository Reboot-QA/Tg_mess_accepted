@echo off
chcp 65001 >nul
cd /d "%~dp0"

set TASK_NAME=TelegramWeChatPush
set SCRIPT=%~dp0start_background.bat

echo 将注册开机自启计划任务: %TASK_NAME%
echo 脚本路径: %SCRIPT%
echo.

schtasks /Create /TN "%TASK_NAME%" /TR "\"%SCRIPT%\"" /SC ONLOGON /RL HIGHEST /F
if errorlevel 1 (
    echo 注册失败，请右键「以管理员身份运行」此脚本
    pause
    exit /b 1
)

echo.
echo 已注册开机自启。可在「任务计划程序」中查看或删除任务 %TASK_NAME%
pause
