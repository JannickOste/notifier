
class MessageDispatcher:
    """
    Base class for message dispatchers.
    This class defines the interface that all message dispatcher classes must implement.
    """
    def __init__(self, *args, **kwargs):
        pass

    async def dispatch(self, payload: dict):
        """
        Dispatch the message to the appropriate bot.
        This method should be overridden by subclasses to implement specific dispatching logic.
        """
        raise NotImplementedError("Subclasses must implement the dispatch method.")