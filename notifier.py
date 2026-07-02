"""消息推送：支持 Server酱（免费）、企业微信群机器人（免费）、PushPlus。"""

import logging

import requests

logger = logging.getLogger(__name__)


def send_notification(push_cfg: dict, title: str, content: str) -> bool:
    provider = push_cfg.get("provider", "serverchan")

    if provider == "serverchan":
        return send_serverchan(push_cfg.get("serverchan", {}), title, content)
    if provider == "wecom":
        return send_wecom(push_cfg.get("wecom", {}), title, content)
    if provider == "pushplus":
        from pushplus import send_pushplus

        cfg = push_cfg.get("pushplus", {})
        return send_pushplus(
            token=cfg.get("token", ""),
            title=title,
            content=content,
            template=cfg.get("template", "html"),
        )

    logger.error("未知推送方式: %s，请在 config.yaml 中设置 push.provider", provider)
    return False


def send_serverchan(cfg: dict, title: str, content: str) -> bool:
    sendkey = cfg.get("sendkey", "")
    if not sendkey or sendkey == "your_sendkey":
        logger.error("Server酱 sendkey 未配置")
        return False

    try:
        response = requests.post(
            f"https://sctapi.ftqq.com/{sendkey}.send",
            data={"title": title[:100], "desp": content},
            timeout=15,
        )
        response.raise_for_status()
        result = response.json()
        if result.get("code") == 0:
            logger.info("Server酱 推送成功: %s", title)
            return True

        logger.error("Server酱 推送失败: %s", result.get("message", result))
        return False
    except requests.RequestException as exc:
        logger.error("Server酱 请求异常: %s", exc)
        return False


def send_wecom(cfg: dict, title: str, content: str) -> bool:
    webhook = (cfg.get("webhook", "") or "").strip()
    if not webhook or "YOUR_KEY" in webhook or webhook == "your_webhook_url":
        logger.error("企业微信 webhook 未配置，请在 config.yaml 填写 push.wecom.webhook")
        return False
    if not webhook.startswith("https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key="):
        logger.error("企业微信 webhook 格式不正确，请从群机器人页面复制完整地址")
        return False

    text = f"{title}\n{content}".replace("**", "")
    try:
        response = requests.post(
            webhook,
            json={
                "msgtype": "text",
                "text": {
                    "content": text[:2048],
                },
            },
            timeout=15,
        )
        response.raise_for_status()
        result = response.json()
        if result.get("errcode") == 0:
            logger.info("企业微信 推送成功: %s", title)
            return True

        logger.error("企业微信 推送失败: %s", result.get("errmsg", result))
        return False
    except requests.RequestException as exc:
        logger.error("企业微信 请求异常: %s", exc)
        return False
