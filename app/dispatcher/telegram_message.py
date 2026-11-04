import asyncio
import logging
import os
from typing import override

import aiohttp

from base.message_dispatcher import MessageDispatcherBase


class TelegramMessageDispatcher(MessageDispatcherBase):
    __token: str | None = None
    __chat_id: str | None = None

    __max_retries: int = 5
    __timeout: int = 15

    @property
    def api_url(self) -> str:
        if self.__token is None:
            raise ValueError("Telegram bot token is not set")
        
        return f"https://api.telegram.org/bot{self.__token}/sendMessage"

    def __init__(self):
        self.__token = os.getenv("TELEGRAM_TOKEN")
        self.__chat_id = os.getenv("TELEGRAM_CHAT_ID")

    @override
    async def dispatch(self, message):
        payload = {
            "chat_id": self.__chat_id,
            "text": message,
            "parse_mode": "HTML",
            "disable_web_page_preview": "true",
        }

        timeout = aiohttp.ClientTimeout(total=self.__timeout)

        async with aiohttp.ClientSession(timeout=timeout) as session:
            for attempt in range(self.__max_retries):
                try:
                    async with session.post(
                        self.api_url,
                        data=payload,
                    ) as response:

                        result = await response.json(content_type=None)

                        if response.status in (400, 401, 403):
                            raise RuntimeError(
                                f"Telegram HTTP {response.status}: {result}"
                            )

                        if response.status >= 400:
                            raise RuntimeError(
                                f"Telegram HTTP {response.status}: {result}"
                            )

                        if not result.get("ok"):
                            raise RuntimeError(
                                f"Telegram API error: {result}"
                            )

                    return

                except (aiohttp.ClientError, asyncio.TimeoutError, RuntimeError) as exc:
                    logging.warning(
                        "Telegram send failed (attempt %s/%s): %s",
                        attempt + 1,
                        self.__max_retries,
                        exc,
                    )

                    if attempt == self.__max_retries - 1:
                        raise

                    await asyncio.sleep(min(2 ** attempt, 20))

