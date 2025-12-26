import logging
from aiogram import Bot
from aiogram.enums import ChatMemberStatus
from app.domain.interfaces import AbstractChannelChecker

logger = logging.getLogger(__name__)

class TelegramChannelChecker(AbstractChannelChecker):
    def __init__(self, bot: Bot):
        self.bot = bot

    async def is_member(self, user_id: int, channel_id: str) -> bool:
        try:
            member = await self.bot.get_chat_member(chat_id=channel_id, user_id=user_id)
            is_member = member.status in [
                ChatMemberStatus.MEMBER,
                ChatMemberStatus.ADMINISTRATOR,
                ChatMemberStatus.CREATOR
            ]
            logger.info(f"Subscription check: user={user_id}, channel={channel_id}, status={member.status}, is_member={is_member}")
            return is_member
        except Exception as e:
            if "chat not found" in str(e).lower():
                logger.error(f"CRITICAL: Bot cannot find channel {channel_id}. Is the bot an admin there?")
            else:
                logger.error(f"Error checking subscription: user={user_id}, channel={channel_id}, error={e}")
            return False
