import asyncio
import json
import logging
from abc import abstractmethod

from base.monitor import MonitorBase


logger = logging.getLogger(__name__)


class JournalMonitorBase(MonitorBase):

    def __init__(self, journal_target: str):
        super().__init__()
        self.__journal_target = journal_target

    async def monitor(self) -> None:
        command = [
            "journalctl",
            "--follow",
            "--no-pager",
            "--output=json",
            "-n", "0",
            "-t", self.__journal_target,
        ]

        logger.info(
            "Starting journal reader for: %s",
            self.__journal_target,
        )

        while True:
            proc = None

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

                        await self._on_event("message", message)

                    except json.JSONDecodeError:
                        logger.warning("Invalid journal JSON")

                    except Exception:
                        logger.exception(
                            "Could not process journal data"
                        )

                logger.warning("journalctl exited; restarting")

            except asyncio.CancelledError:
                logger.info("Journal reader stopped")

                if proc is not None and proc.returncode is None:
                    proc.terminate()
                    await proc.wait()

                raise

            except Exception:
                logger.exception("Journal reader failed")

            finally:
                if proc is not None and proc.returncode is None:
                    proc.terminate()
                    await proc.wait()

            await asyncio.sleep(5)

    @abstractmethod
    async def _on_event(self, type, eventData) -> None:
        raise NotImplementedError