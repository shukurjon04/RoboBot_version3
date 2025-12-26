from typing import Callable, Dict, Any, Awaitable
from aiogram import BaseMiddleware
from aiogram.types import Message, CallbackQuery, TelegramObject

from app.domain.repositories import AbstractUserRepository
from app.infrastructure.database.db_helper import get_db_session, session_factory
from app.infrastructure.repositories.sqlalchemy import SQLAlchemyUserRepository, SQLAlchemyReferralRepository
from app.use_cases.registration import RegistrationService

class UserMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any]
    ) -> Any:
        # Determine user_id
        user = data.get("event_from_user")
        if not user:
            return await handler(event, data)

        async with session_factory() as session:
            user_repo = SQLAlchemyUserRepository(session)
            referral_repo = SQLAlchemyReferralRepository(session)
            
            # Fetch DB user
            db_user = await user_repo.get_user(user.id)
            
            data["session"] = session
            data["user_repo"] = user_repo
            data["referral_repo"] = referral_repo
            data["db_user"] = db_user
            
            return await handler(event, data)
