#!/usr/bin/env bash
set -euo pipefail

if [ "$(id -u)" -ne 0 ]; then
  echo "请使用 root 运行: sudo ./install_service.sh"
  exit 1
fi

ROOT="$(cd "$(dirname "$0")" && pwd)"
SERVICE_USER="${SUDO_USER:-$(logname 2>/dev/null || echo root)}"
SERVICE_NAME="telegram-wechat-push"
UNIT_PATH="/etc/systemd/system/${SERVICE_NAME}.service"

if [ ! -f "${ROOT}/venv/bin/python" ]; then
  echo "请先运行: ./install.sh"
  exit 1
fi

sed \
  -e "s|__USER__|${SERVICE_USER}|g" \
  -e "s|__WORKDIR__|${ROOT}|g" \
  "${ROOT}/deploy/telegram-wechat-push.service" > "${UNIT_PATH}"

systemctl daemon-reload
systemctl enable "${SERVICE_NAME}"
systemctl restart "${SERVICE_NAME}"

echo "服务已安装并启动: ${SERVICE_NAME}"
echo
echo "常用命令:"
echo "  sudo systemctl status ${SERVICE_NAME}"
echo "  sudo journalctl -u ${SERVICE_NAME} -f"
echo "  sudo systemctl restart ${SERVICE_NAME}"
