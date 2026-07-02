#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")" && pwd)"
cd "$ROOT"

if ! command -v python3 >/dev/null 2>&1; then
  echo "请先安装 Python 3: sudo apt install python3 python3-venv python3-pip"
  exit 1
fi

if [ ! -d "venv" ]; then
  echo "[1/3] 创建虚拟环境..."
  python3 -m venv venv
fi

echo "[2/3] 安装依赖..."
# shellcheck disable=SC1091
source venv/bin/activate
pip install -U pip -q
pip install -r requirements.txt -q

if [ ! -f "config.yaml" ]; then
  echo "[3/3] 创建 config.yaml..."
  cp config.example.yaml config.yaml
  echo "请编辑 config.yaml 填写 Telegram 和推送配置"
else
  echo "[3/3] 已存在 config.yaml，跳过"
fi

echo
echo "安装完成。下一步:"
echo "  1. 编辑 config.yaml"
echo "  2. 首次登录: ./start.sh"
echo "  3. 测试推送: ./test_push.sh"
echo "  4. 安装服务: sudo ./install_service.sh"
