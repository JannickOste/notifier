from app.base.message_dispatcher import MessageDispatcherBase
from app.dispatcher.telegram_message import TelegramMessageDispatcher
from app.base.monitor import MonitorBase

import asyncio

import sys
import logging

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
    force=True,
)


logger = logging.getLogger("notifier")


async def loadDispatchers():
    message_dispatcher_modules: list[MessageDispatcherBase] = [
        TelegramMessageDispatcher
    ]

    loaded_modules = []
    for dispatcher in message_dispatcher_modules:
        instance = None
        try:
            instance = dispatcher()
        except Exception:
            logger.error("Failed loading message dispatcher %s", dispatcher.__class__.__name__)
        finally:
            if instance is not None:
                loaded_modules.append(instance)

    return loaded_modules


async def main(monitors: list[MonitorBase] = []):
    logger.info("Starting notification bot...")

    if not len(monitors):
        logger.error("No monitoring services specified, exitting application")
        sys.exit(-1)
    
    dispatchers = await loadDispatchers()
    logger.info("Found %s message dispatcher", len(dispatchers))
    if not len(dispatchers):
        logger.warning("No message dispatchers found, logs will be continued to be monitored but no notifications will be dispatched")

    




if __name__ == "__main__":
    asyncio.run(main())