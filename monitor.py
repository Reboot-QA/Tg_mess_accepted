"""Telegram 消息监控 -> 推送到微信/企业微信。支持 Linux 服务器与 Windows 无影云桌面 7x24 运行。"""

from __future__ import annotations

import asyncio
import html
import logging
import sys
import time
from pathlib import Path
import yaml
from telethon import TelegramClient, events
from telethon.tl.types import Message

from notifier import send_notification

ROOT = Path(__file__).resolve().parent
CONFIG_PATH = ROOT / "config.yaml"

_last_push_at: dict[int, float] = {}


def setup_logging(log_file: str) -> None:
    log_path = ROOT / log_file
    log_path.parent.mkdir(parents=True, exist_ok=True)

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        handlers=[
            logging.FileHandler(log_path, encoding="utf-8"),
            logging.StreamHandler(sys.stdout),
        ],
    )


def load_config() -> dict:
    if not CONFIG_PATH.exists():
        print("未找到 config.yaml，请先复制 config.example.yaml 并填写配置")
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


def message_preview(message: Message) -> str:
    if message.text:
        return message.text
    if message.photo:
        return "[图片]"
    if message.video:
        return "[视频]"
    if message.document:
        return "[文件]"
    if message.sticker:
        return "[贴纸]"
    if message.voice:
        return "[语音]"
    return "[非文本消息]"


def match_keywords(text: str, keywords: list[str]) -> bool:
    if not keywords:
        return True
    return any(keyword in text for keyword in keywords)


def should_push(chat_id: int, cooldown: int) -> bool:
    now = time.time()
    last = _last_push_at.get(chat_id, 0)
    if now - last < cooldown:
        return False
    _last_push_at[chat_id] = now
    return True


async def get_sender_name(event) -> str:
    sender = await event.get_sender()
    if sender is None:
        return "未知"
    parts = [getattr(sender, "first_name", None), getattr(sender, "last_name", None)]
    name = " ".join(part for part in parts if part)
    return name or getattr(sender, "title", None) or getattr(sender, "username", None) or "未知"


async def main() -> None:
    config = load_config()
    tg_cfg = config["telegram"]
    push_cfg = config.get("push", config.get("pushplus", {}))
    if "token" in push_cfg and "provider" not in push_cfg:
        push_cfg = {"provider": "pushplus", "pushplus": push_cfg}
    app_cfg = config.get("app", {})

    setup_logging(app_cfg.get("log_file", "logs/push.log"))
    logger = logging.getLogger(__name__)

    watch_chats = tg_cfg.get("watch_chats") or None
    keywords = tg_cfg.get("keywords") or []
    cooldown = int(app_cfg.get("cooldown_seconds", 3))
    proxy = build_proxy(tg_cfg.get("proxy", {}))

    client = TelegramClient(
        str(ROOT / tg_cfg["session_name"]),
        tg_cfg["api_id"],
        tg_cfg["api_hash"],
        proxy=proxy,
    )

    @client.on(events.NewMessage(chats=watch_chats))
    async def on_new_message(event: events.NewMessage.Event) -> None:
        text = message_preview(event.message)
        if not match_keywords(text, keywords):
            return

        chat = await event.get_chat()
        chat_name = getattr(chat, "title", None) or getattr(chat, "first_name", "私聊")
        sender_name = await get_sender_name(event)
        chat_id = event.chat_id

        if not should_push(chat_id, cooldown):
            logger.debug("跳过推送（冷却中）: %s", chat_name)
            return

        title = f"Telegram: {chat_name}"
        if push_cfg.get("provider", "serverchan") == "pushplus":
            content = (
                f"<b>来源</b>: {html.escape(chat_name)}<br>"
                f"<b>发送者</b>: {html.escape(sender_name)}<br>"
                f"<b>内容</b>: {html.escape(text[:500])}"
            )
        else:
            content = (
                f"**来源**: {chat_name}\n"
                f"**发送者**: {sender_name}\n"
                f"**内容**: {text[:500]}"
            )

        logger.info("新消息 [%s] %s: %s", chat_name, sender_name, text[:80])
        send_notification(push_cfg, title=title, content=content)

    logger.info("监控范围: %s", watch_chats or "全部可见聊天")
    logger.info("关键词过滤: %s", keywords or "无")

    retry_delay = int(app_cfg.get("reconnect_delay_seconds", 10))
    while True:
        try:
            logger.info("正在启动 Telegram 监控...")
            await client.start()
            me = await client.get_me()
            logger.info("已登录: %s (@%s)", me.first_name, me.username or "无用户名")
            logger.info("监控运行中，按 Ctrl+C 停止")

            await client.run_until_disconnected()
            logger.warning("Telegram 连接已断开")
        except Exception:
            logger.exception("监控运行异常")
        finally:
            if client.is_connected():
                await client.disconnect()

        logger.warning("%d 秒后尝试重连...", retry_delay)
        await asyncio.sleep(retry_delay)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n已停止监控")
