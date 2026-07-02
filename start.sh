#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")" && pwd)"
cd "$ROOT"

if [ ! -d "venv" ]; then
  echo "请先运行: ./install.sh"
  exit 1
fi

if [ ! -f "config.yaml" ]; then
  echo "未找到 config.yaml，请先运行: ./install.sh"
  exit 1
fi

# shellcheck disable=SC1091
source venv/bin/activate
exec python monitor.py
