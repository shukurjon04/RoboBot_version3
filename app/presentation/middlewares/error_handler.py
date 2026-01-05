import logging
from typing import Callable, Dict, Any, Awaitable
from aiogram import BaseMiddleware
from aiogram.types import Message, CallbackQuery, TelegramObject

logger = logging.getLogger(__name__)

class ErrorHandlingMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any]
    ) -> Any:
        try:
            return await handler(event, data)
        except Exception as e:
            logger.error(f"Unhandled exception in middleware: {e}", exc_info=True)
            
            # User facing error message
            error_text = (
                "⚠️ <b>Xatolik yuz berdi!</b>\n\n"
                "Kechirasiz, tizimda qandaydir muammo paydo bo'ldi. "
                "Iltimos, birozdan so'ng qayta urinib ko'ring yoki adminlarga xabar bering."
            )
            
            try:
                if isinstance(event, Message):
                    await event.answer(error_text, parse_mode="HTML")
                elif isinstance(event, CallbackQuery):
                    await event.message.answer(error_text, parse_mode="HTML")
                    await event.answer()
            except Exception as send_err:
                logger.error(f"Failed to send error message to user: {send_err}")
            
            # We suppress the exception so the bot keeps running, 
            # but we've logged it above.
            return None
