@echo off
chcp 65001 >nul
cd /d "%~dp0"

if not exist "venv\Scripts\python.exe" (
    echo [1/3] 创建虚拟环境...
    python -m venv venv
    if errorlevel 1 (
        echo 请先安装 Python 3.10+ 并勾选 Add to PATH
        pause
        exit /b 1
    )
)

echo [2/3] 安装依赖...
call venv\Scripts\activate.bat
pip install -r requirements.txt -q

if not exist "config.yaml" (
    echo [提示] 未找到 config.yaml，正在从模板复制...
    copy config.example.yaml config.yaml >nul
    echo 请编辑 config.yaml 填写 api_id、api_hash、pushplus token 后重新运行
    notepad config.yaml
    pause
    exit /b 0
)

echo [3/3] 启动监控...
python monitor.py
pause
