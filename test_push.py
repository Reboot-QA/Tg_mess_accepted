"""测试推送配置是否正常。用法: python test_push.py"""

import sys
from pathlib import Path

import yaml

from notifier import send_notification

ROOT = Path(__file__).resolve().parent
CONFIG_PATH = ROOT / "config.yaml"


def main() -> None:
    if not CONFIG_PATH.exists():
        print("未找到 config.yaml")
        sys.exit(1)

    with CONFIG_PATH.open(encoding="utf-8") as f:
        config = yaml.safe_load(f)

    push_cfg = config.get("push", {})
    provider = push_cfg.get("provider", "unknown")
    print(f"当前推送方式: {provider}")
    print("正在发送测试消息...")

    ok = send_notification(
        push_cfg,
        title="Telegram监控测试",
        content="**来源**: 测试\n**发送者**: 系统\n**内容**: 如果你收到这条，说明推送配置正常",
    )

    if ok:
        print("推送成功！请检查微信/企业微信是否收到消息。")
    else:
        print("推送失败，请查看上方错误信息。")
        sys.exit(1)


if __name__ == "__main__":
    main()
