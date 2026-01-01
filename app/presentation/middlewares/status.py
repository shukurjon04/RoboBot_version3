from typing import Callable, Dict, Any, Awaitable
from aiogram import BaseMiddleware, Bot
from aiogram.types import Message, TelegramObject, CallbackQuery
from app.domain.enums import UserStatus
from app.infrastructure.repositories.sqlalchemy import SQLAlchemyChannelRepository
from app.infrastructure.telegram.checker import TelegramChannelChecker
from app.use_cases.subscription import SubscriptionService
from app.presentation.keyboards.registration import check_subscription_kb
from app.config.settings import settings

class CheckStatusMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any]
    ) -> Any:
        db_user = data.get("db_user")
        bot: Bot = data.get("bot")
        session = data.get("session")
        
        # If no user yet, allow proceeding (e.g. for /start to create user)
        if not db_user:
            return await handler(event, data)
            
        # Bypass admins
        if db_user.telegram_id in settings.ADMIN_IDS:
            return await handler(event, data)
            
        if db_user.status == UserStatus.BLOCKED:
            return
            
        # Check for exemption: /start command or check_subscription callback
        is_start_cmd = isinstance(event, Message) and event.text and event.text.startswith("/start")
        is_check_cb = isinstance(event, CallbackQuery) and event.data == "check_subscription"
        
        if is_start_cmd or is_check_cb:
            return await handler(event, data)

        # For all other cases, enforce channel subscription
        channel_repo = SQLAlchemyChannelRepository(session)
        checker = TelegramChannelChecker(bot)
        sub_service = SubscriptionService(channel_repo, checker)
        
        is_subbed, unsubscribed = await sub_service.check_user_subscription(db_user.telegram_id)
        
        if not is_subbed:
            text = (
                "⚠️ <b>Botdan foydalanish uchun kanallarga a'zo bo'lishingiz shart!</b>\n\n"
                "Iltimos, tanlov yangiliklaridan xabardor bo'lish va imkoniyatlarni o'tkazib yubormaslik uchun quyidagi kanallarga obuna bo'ling:"
            )
            
            if isinstance(event, Message):
                await event.answer(text, parse_mode="HTML", reply_markup=check_subscription_kb(unsubscribed))
            elif isinstance(event, CallbackQuery):
                await event.message.answer(text, parse_mode="HTML", reply_markup=check_subscription_kb(unsubscribed))
                await event.answer()
            return

        return await handler(event, data)
