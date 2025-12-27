import asyncio
import logging
import sys

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage 
from aiogram.enums import ParseMode

from app.config.settings import settings
# from app.infrastructure.cache.factory import make_redis_storage
from app.presentation.middlewares.user import UserMiddleware
from app.presentation.middlewares.status import CheckStatusMiddleware
from app.presentation.handlers import registration, user, admin, profile
from app.infrastructure.database.db_helper import engine, session_factory
from app.use_cases.scheduler import WebinarSchedulerService
from app.infrastructure.repositories.sqlalchemy import SQLAlchemyUserRepository

async def main():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
    )

    # Initialize Bot
    bot = Bot(token=settings.BOT_TOKEN.get_secret_value())
    
    # Initialize Storage
    # Initialize Storage
    storage = MemoryStorage()

    dp = Dispatcher(storage=storage)

    # Register Middlewares
    dp.update.middleware(UserMiddleware())
    dp.message.middleware(CheckStatusMiddleware())
    dp.callback_query.middleware(CheckStatusMiddleware())

    # Register Routers
    dp.include_router(registration.router)
    dp.include_router(user.router)
    dp.include_router(profile.router)
    dp.include_router(admin.router)

    # Initialize and start webinar scheduler
    # Create a dummy user_repo for scheduler (it gets its own session)
    async with session_factory() as session:
        user_repo = SQLAlchemyUserRepository(session)
    
    scheduler_service = WebinarSchedulerService(session_factory, bot, user_repo)
    scheduler_service.start()
    
    logging.info("Starting bot...")
    try:
        await bot.delete_webhook(drop_pending_updates=True)
        await dp.start_polling(bot)
    finally:
        scheduler_service.shutdown()

if __name__ == "__main__":
    try:
        if sys.platform == "win32":
            asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logging.info("Bot stopped!")
