from abc import abstractmethod

from app.base.message_dispatcher import MessageDispatcherBase

class MonitorBase:
    """
    Base class for monitors.
    This class defines the interface that all monitor classes must implement.
    """

    def _on_event(self, type: str, eventData: dict):
        raise NotImplementedError("Subclasses must implement the _on_event method.")

    @abstractmethod
    async def monitor(self):
        raise NotImplementedError("Subclasses must implement the monitor method.")
    