from abc import ABC, abstractmethod

class AbstractChannelChecker(ABC):
    @abstractmethod
    async def is_member(self, user_id: int, channel_id: str) -> bool:
        pass
