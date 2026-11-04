
from abc import abstractmethod
import asyncio
import json
import logging
from base.monitor import MonitorBase



class JournalMonitorBase(MonitorBase):

    def __init__(self, journal_target: str):
        super().__init__()
        self.__journal_target = journal_target
        
    async def monitor(self):
        command = [
            "journalctl",
            "--follow",
            "--no-pager",
            "--output=json",
            "-n", "0",
            "-t", self.__journal_target,
        ]

        logging.info(
            "Starting journal reader for: %s",
            self.__journal_target
        )

        while True:
            try:
                proc = await asyncio.create_subprocess_exec(
                    *command,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.DEVNULL,
                )

                assert proc.stdout is not None

                async for line in proc.stdout:
                    try:
                        entry = json.loads(line)
                        message = entry.get("MESSAGE", "")

                        if isinstance(message, list):
                            message = bytes(message).decode(
                                errors="replace"
                            )

                        self._on_event("message", message)

                    except json.JSONDecodeError:
                        logging.warning("Invalid journal JSON")

                    except Exception:
                        logging.exception(
                            "Could not process journal data"
                        )

                logging.warning("journalctl exited; restarting")

            except Exception:
                logging.exception("Journal reader failed")

            await asyncio.sleep(5)

    @abstractmethod
    def _on_event(self, type, eventData) -> None:
        raise NotImplementedError
    