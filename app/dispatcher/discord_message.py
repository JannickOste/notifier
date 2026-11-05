
import asyncio
import logging
import os
from typing import override

import re
from html import unescape

import aiohttp

from base.message_dispatcher import MessageDispatcherBase
from formatter.html_to_discord import html_to_discord

class DiscordMessageDispatcher(MessageDispatcherBase):
    __token: str | None = None
    __channel_id: str | None = None

    __max_retries: int = 5
    __timeout: int = 15

    @property
    def api_url(self) -> str:
        if self.__token is None:
            raise ValueError("Discord bot token is not set")

        if self.__channel_id is None:
            raise ValueError("Discord channel ID is not set")

        return (
            f"https://discord.com/api/v10/"
            f"channels/{self.__channel_id}/messages"
        )

    def __init__(self):
        self.__token = os.getenv("DISCORD_BOT_TOKEN")
        self.__channel_id = os.getenv("DISCORD_CHANNEL_ID")

    
    @override
    async def dispatch(self, message):
        payload = {
            "content": DiscordMessageDispatcher.html_to_discord(message),
        }

        headers = {
            "Authorization": f"Bot {self.__token}",
            "Content-Type": "application/json",
        }

        timeout = aiohttp.ClientTimeout(total=self.__timeout)

        async with aiohttp.ClientSession(timeout=timeout) as session:
            for attempt in range(self.__max_retries):
                try:
                    async with session.post(
                        self.api_url,
                        json=payload,
                        headers=headers,
                    ) as response:

                        result = await response.json(content_type=None)

                        if response.status in (400, 401, 403, 404):
                            raise RuntimeError(
                                f"Discord HTTP {response.status}: {result}"
                            )

                        if response.status == 429:
                            retry_after = result.get("retry_after", 1)
                            raise RuntimeError(
                                f"Discord rate limited: retry after {retry_after}s"
                            )

                        if response.status >= 500:
                            raise RuntimeError(
                                f"Discord HTTP {response.status}: {result}"
                            )

                        if response.status >= 400:
                            raise RuntimeError(
                                f"Discord HTTP {response.status}: {result}"
                            )

                    return

                except (
                    aiohttp.ClientError,
                    asyncio.TimeoutError,
                    RuntimeError,
                ) as exc:
                    logging.warning(
                        "Discord send failed (attempt %s/%s): %s",
                        attempt + 1,
                        self.__max_retries,
                        exc,
                    )

                    if attempt == self.__max_retries - 1:
                        raise

                    await asyncio.sleep(min(2 ** attempt, 20))
