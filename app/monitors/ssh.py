import html
import re
from typing import override

from base.journal_monitor import JournalMonitorBase


class SSHMonitor(JournalMonitorBase):

    flags =  {
        "connections": True,
        "failures": True,
        "success": True,
        "disconnects": True,
    }
    def __init__(self):
        super().__init__("sshd-session")

    @override
    async def _on_event(self, type, eventData) -> None:
        """Handle incoming events and invoke the appropriate async handler."""

        if type == "message":
            return await self.__on_message_event(eventData)

        handlers = {
            "connections": None,
            "success": self.__on_connection_success_event,
            "failures": self.__on_connection_failed_event,
            "disconnects": self.__on_disconnect_event,
        }

        handler = handlers.get(type)

        if handler is not None and self.flags.get(type):
            return await handler(eventData)

        return None

    async def __on_message_event(self, message) -> None:
        """Match incoming journal messages against SSH event patterns."""

        patterns = [
            (
                "failures",
                re.compile(
                    r"\bFailed (?P<method>password|publickey|keyboard-interactive(?:/pam)?) "
                    r"for (?:(?:invalid user) )?(?P<user>\S+) "
                    r"from (?P<ip>\S+) port (?P<port>\d+)"
                ),
            ),
            (
                "failures",
                re.compile(
                    r"\bConnection reset by authenticating user "
                    r"(?P<user>\S+) (?P<ip>\S+) port (?P<port>\d+)"
                    r"(?:\s+\[preauth\])?"
                ),
            ),
            (
                "failures",
                re.compile(
                    r"\bConnection reset by peer"
                    r"(?:\s+\[preauth\])?"
                ),
            ),
            (
                "success",
                re.compile(
                    r"\bAccepted (?P<method>\S+) for (?P<user>\S+) "
                    r"from (?P<ip>\S+) port (?P<port>\d+)"
                ),
            ),
            (
                "disconnects",
                re.compile(
                    r"\bDisconnected from "
                    r"(?:user\s+(?P<user>\S+)\s+)?"
                    r"(?P<ip>\S+) port (?P<port>\d+)"
                ),
            ),
        ]

        for event_type, pattern in patterns:
            if payload := pattern.search(message):
                return await self._on_event(
                    event_type,
                    payload.groupdict(),
                )

        return None

    async def __on_connection_failed_event(self, eventData: dict):
        """Dispatch a failed SSH authentication event."""

        await self._dispatch_message((
                "🔴 <b>SSH Authentication Failed</b>\n"
                f"User: <code>{html.escape(eventData.get('user') or 'unknown')}</code>\n"
                f"Method: <code>{html.escape(eventData.get('method') or 'unknown')}</code>\n"
                f"Source: <code>{html.escape(eventData.get('ip') or 'unknown')}:"
                f"{html.escape(eventData.get('port') or 'unknown')}</code>"
            )
        )

    async def __on_connection_success_event(self, eventData: dict):
        """Dispatch a successful SSH authentication event."""

        await self._dispatch_message((
                "🟢 <b>SSH Connection Established</b>\n"
                f"User: <code>{html.escape(eventData.get('user') or 'unknown')}</code>\n"
                f"Method: <code>{html.escape(eventData.get('method') or 'unknown')}</code>\n"
                f"Source: <code>{html.escape(eventData.get('ip') or 'unknown')}:"
                f"{html.escape(eventData.get('port') or 'unknown')}</code>"
            )
        )

    async def __on_disconnect_event(self, eventData: dict):
        """Dispatch a disconnected SSH session event."""

        await self._dispatch_message(("🟠 <b>SSH Session Disconnected</b>\n"
                f"User: <code>{html.escape(eventData.get('user') or 'unknown')}</code>\n"
                f"Source: <code>{html.escape(eventData.get('ip') or 'unknown')}:"
                f"{html.escape(eventData.get('port') or 'unknown')}</code>"
            )
        )