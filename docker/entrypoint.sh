#!/bin/sh
set -e

mkdir -p /app/data/logs /app/data/sessions

if [ ! -f /app/data/config.yaml ]; then
  echo "错误: 未找到 /app/data/config.yaml"
  echo "请先在宿主机运行: ./docker/setup.sh"
  exit 1
fi

ln -sf /app/data/config.yaml /app/config.yaml

exec "$@"
