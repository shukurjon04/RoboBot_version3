from typing import List, Tuple
from app.domain.repositories import AbstractChannelRepository
from app.domain.interfaces import AbstractChannelChecker
from app.infrastructure.database.models import Channel

class SubscriptionService:
    def __init__(self, channel_repo: AbstractChannelRepository, checker: AbstractChannelChecker):
        self.channel_repo = channel_repo
        self.checker = checker

    async def get_required_channels(self) -> List[Channel]:
        return await self.channel_repo.get_all_active()

    async def check_user_subscription(self, user_id: int) -> Tuple[bool, List[Channel]]:
        """
        Returns (is_subscribed_to_all, list_of_unsubscribed_channels)
        """
        channels = await self.channel_repo.get_all_active()
        unsubscribed = []
        
        for channel in channels:
            is_member = await self.checker.is_member(user_id, channel.channel_id)
            if not is_member:
                unsubscribed.append(channel)
        
        return len(unsubscribed) == 0, unsubscribed
