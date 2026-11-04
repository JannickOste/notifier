from abc import abstractmethod
import asyncio

class MonitorBase:
    """
    Base class for monitors.
    This class defines the interface that all monitor classes must implement.
    """

    __message_dispatchers: list = []

    def _on_event(self, type: str, eventData: dict):
        raise NotImplementedError("Subclasses must implement the _on_event method.")

    @abstractmethod
    async def monitor(self):
        raise NotImplementedError("Subclasses must implement the monitor method.")

    def setMessageDispatcher(self, *dispatchers: list):
        self.__message_dispatchers = dispatchers

    async def _dispatch_message(self, payload) -> None:
        """
        Dispatch a message asynchronously to all registered dispatchers.
        All dispatchers are awaited concurrently.
        """
        if not self.__message_dispatchers:
            return

        await asyncio.gather(
            *(
                dispatcher.dispatch(payload)
                for dispatcher in self.__message_dispatchers
            )
        )