from typing import Callable, Dict, Any, Awaitable
from aiogram import BaseMiddleware
from aiogram.types import Message, CallbackQuery, TelegramObject

class ChatTypeMiddleware(BaseMiddleware):
    """
    Middleware to restrict bot functionality to private chats only.
    Ignores all messages and callbacks from groups, supergroups, and channels.
    """
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any]
    ) -> Any:
        # Extract chat information from the event
        chat = None
        if isinstance(event, Message):
            chat = event.chat
        elif isinstance(event, CallbackQuery) and event.message:
            chat = event.message.chat
        
        # If we can't determine chat type, allow (fail-safe)
        if not chat:
            return await handler(event, data)
        
        # Only allow private chats
        if chat.type == "private":
            return await handler(event, data)
        
        # Silently ignore messages from groups, supergroups, and channels
        # No response is sent to avoid spam in group chats
        return None
