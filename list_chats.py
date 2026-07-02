"""列出 Telegram 账号可见的群/频道，用于填写 config.yaml 中的 watch_chats。"""

import asyncio
import sys
from pathlib import Path

import yaml
from telethon import TelegramClient

ROOT = Path(__file__).resolve().parent
CONFIG_PATH = ROOT / "config.yaml"


def load_config() -> dict:
    if not CONFIG_PATH.exists():
        print("请先复制 config.example.yaml 为 config.yaml 并填写配置")
        sys.exit(1)
    with CONFIG_PATH.open(encoding="utf-8") as f:
        return yaml.safe_load(f)


def build_proxy(proxy_cfg: dict):
    if not proxy_cfg.get("enabled"):
        return None

    import socks

    proxy_type = socks.SOCKS5 if proxy_cfg.get("type", "socks5") == "socks5" else socks.HTTP
    return (
        proxy_type,
        proxy_cfg["host"],
        int(proxy_cfg["port"]),
        True,
        proxy_cfg.get("username") or None,
        proxy_cfg.get("password") or None,
    )


async def main() -> None:
    cfg = load_config()["telegram"]
    proxy = build_proxy(cfg.get("proxy", {}))

    client = TelegramClient(
        str(ROOT / cfg["session_name"]),
        cfg["api_id"],
        cfg["api_hash"],
        proxy=proxy,
    )

    await client.start()
    print("\n=== 你的 Telegram 聊天列表 ===\n")
    print(f"{'ID':<20} {'类型':<10} 名称")
    print("-" * 60)

    async for dialog in client.iter_dialogs():
        entity = dialog.entity
        chat_type = type(entity).__name__
        print(f"{dialog.id:<20} {chat_type:<10} {dialog.name}")

    print("\n将需要的 ID 填入 config.yaml 的 watch_chats 列表")
    await client.disconnect()


if __name__ == "__main__":
    asyncio.run(main())
