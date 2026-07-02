#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

mkdir -p data/logs data/sessions

if [ ! -f "data/config.yaml" ]; then
  cp config.example.yaml data/config.yaml
  echo "已创建 data/config.yaml（Docker 版路径）"
else
  echo "data/config.yaml 已存在，跳过"
fi

# 确保 Docker 使用 data 目录存放 session 和日志
python3 - <<'PY'
from pathlib import Path
import re

path = Path("data/config.yaml")
text = path.read_text(encoding="utf-8")

text = re.sub(
    r'^(\s*session_name:\s*).*$',
    r'\1"data/sessions/telegram_session"',
    text,
    count=1,
    flags=re.M,
)
text = re.sub(
    r'^(\s*log_file:\s*).*$',
    r'\1"data/logs/push.log"',
    text,
    count=1,
    flags=re.M,
)
path.write_text(text, encoding="utf-8")
print("已设置 session 与日志目录: data/sessions, data/logs")
PY

echo
echo "下一步:"
echo "  1. 编辑 data/config.yaml 填写 Telegram 和推送配置"
echo "  2. 构建镜像: docker compose build"
echo "  3. 首次登录: docker compose --profile login run --rm login"
echo "     （或复制 telegram_session.session 到 data/sessions/）"
echo "  4. 测试推送: docker compose --profile test run --rm test"
echo "  5. 启动服务: docker compose up -d"
