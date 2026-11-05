import asyncio
import os
import sys
import logging

from base.message_dispatcher import MessageDispatcherBase
from dispatcher.telegram_message import TelegramMessageDispatcher
from dispatcher.discord_message import DiscordMessageDispatcher

from base.monitor import MonitorBase
from monitors.ssh import SSHMonitor

message_dispatcher_modules: list[MessageDispatcherBase] = [
    TelegramMessageDispatcher,
    DiscordMessageDispatcher
]

monitoring_modules: list[MonitorBase] = [
    SSHMonitor
]

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
    force=True,
)

logger = logging.getLogger("notifier")
async def loadDispatchers():
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

async def loadMonitors() -> list[MonitorBase]:
    loaded_monitors = []
    for monitor in monitoring_modules:
        instance = None
        try:
            instance = monitor()
        except Exception:
            logger.error("Failed loading message dispatcher %s", monitor.__class__.__name__)
        finally:
            if instance is not None:
                loaded_monitors.append(instance)

    return loaded_monitors


async def main(monitor_modules: list[MonitorBase] = monitoring_modules):
    logger.info("Starting notification bot...")

    if not len(monitor_modules):
        logger.error("No monitoring services specified, exitting application")
        sys.exit(-1)
    
    dispatchers = await loadDispatchers()
    logger.info("Found %s message dispatcher", len(dispatchers))
    if not len(dispatchers):
        logger.warning("No message dispatchers found, logs will be continued to be monitored but no notifications will be dispatched")

    monitors = await loadMonitors()
    logger.info("Found %s monitoring services", len(monitors))

    monitor_tasks = []
    for monitor in monitors:
        monitor.setMessageDispatcher(*dispatchers)

        task = asyncio.create_task(
            monitor.monitor(),
            name=f"{monitor.__class__.__name__}",
        )

        monitor_tasks.append(task)

    logger.info("Started %s monitoring services", len(monitor_tasks))
    try:
        await asyncio.gather(*monitor_tasks)
    except asyncio.CancelledError:
        logger.info("Stopping monitoring services...")

        for task in monitor_tasks:
            task.cancel()

        await asyncio.gather(
            *monitor_tasks,
            return_exceptions=True,
        )

        raise


if __name__ == "__main__":
    asyncio.run(main())