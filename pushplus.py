import logging
from typing import Optional

import requests

logger = logging.getLogger(__name__)


def send_pushplus(
    token: str,
    title: str,
    content: str,
    template: str = "html",
    timeout: int = 15,
) -> bool:
    if not token or token == "your_pushplus_token":
        logger.error("PushPlus token 未配置，请在 config.yaml 中填写")
        return False

    try:
        response = requests.post(
            "https://www.pushplus.plus/send",
            json={
                "token": token,
                "title": title[:100],
                "content": content,
                "template": template,
            },
            timeout=timeout,
        )
        response.raise_for_status()
        result = response.json()
        if result.get("code") == 200:
            logger.info("PushPlus 推送成功: %s", title)
            return True

        logger.error("PushPlus 推送失败: %s", result.get("msg", result))
        return False
    except requests.RequestException as exc:
        logger.error("PushPlus 请求异常: %s", exc)
        return False
