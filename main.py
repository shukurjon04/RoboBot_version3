import asyncio
import logging
import sys
import signal
import os
from pathlib import Path
from logging.handlers import RotatingFileHandler
from datetime import datetime

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage 
from aiogram.enums import ParseMode
from aiogram.exceptions import TelegramNetworkError, TelegramRetryAfter

from app.config.settings import settings
# from app.infrastructure.cache.factory import make_redis_storage
from app.presentation.middlewares.chat_type import ChatTypeMiddleware
from app.presentation.middlewares.user import UserMiddleware
from app.presentation.middlewares.status import CheckStatusMiddleware
from app.presentation.middlewares.error_handler import ErrorHandlingMiddleware
from app.presentation.handlers import registration, user, admin, profile
from app.infrastructure.database.db_helper import engine, session_factory
from app.use_cases.scheduler import WebinarSchedulerService
from app.infrastructure.repositories.sqlalchemy import SQLAlchemyUserRepository


# Global flag for graceful shutdown
shutdown_event = asyncio.Event()


def setup_logging():
    """Configure logging with file rotation and console output"""
    # Create logs directory if it doesn't exist
    logs_dir = Path("logs")
    logs_dir.mkdir(exist_ok=True)
    
    # Create formatters
    detailed_formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    simple_formatter = logging.Formatter(
        "%(asctime)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    
    # Setup root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(simple_formatter)
    root_logger.addHandler(console_handler)
    
    # File handler (all logs) with rotation: max 10MB, keep 5 backup files
    file_handler = RotatingFileHandler(
        logs_dir / "bot.log",
        maxBytes=10_000_000,  # 10MB
        backupCount=5,
        encoding="utf-8"
    )
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(detailed_formatter)
    root_logger.addHandler(file_handler)
    
    # Error file handler (only errors) with rotation
    error_handler = RotatingFileHandler(
        logs_dir / "error.log",
        maxBytes=10_000_000,  # 10MB
        backupCount=5,
        encoding="utf-8"
    )
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(detailed_formatter)
    root_logger.addHandler(error_handler)
    
    return root_logger


def signal_handler(signum, frame):
    """Handle shutdown signals gracefully"""
    sig_name = signal.Signals(signum).name
    logging.info(f"Received signal {sig_name}. Initiating graceful shutdown...")
    shutdown_event.set()


def setup_signal_handlers():
    """Setup signal handlers for graceful shutdown"""
    signal.signal(signal.SIGTERM, signal_handler)
    signal.signal(signal.SIGINT, signal_handler)


async def on_startup(bot: Bot):
    """Actions to perform on bot startup"""
    logging.info("Bot starting up...")
    bot_info = await bot.get_me()
    logging.info(f"Bot @{bot_info.username} (ID: {bot_info.id}) started successfully!")
    
    # Write status file for monitoring
    status_file = Path("logs/bot_status.txt")
    status_file.write_text(f"RUNNING\nStarted: {datetime.now().isoformat()}\nBot: @{bot_info.username}")


async def on_shutdown(bot: Bot, scheduler_service):
    """Actions to perform on bot shutdown"""
    logging.info("Bot shutting down...")
    
    try:
        # Stop scheduler
        if scheduler_service:
            scheduler_service.shutdown()
            logging.info("Scheduler stopped")
        
        # Close bot session
        await bot.session.close()
        logging.info("Bot session closed")
        
        # Update status file
        status_file = Path("logs/bot_status.txt")
        status_file.write_text(f"STOPPED\nStopped: {datetime.now().isoformat()}")
        
    except Exception as e:
        logging.error(f"Error during shutdown: {e}", exc_info=True)


async def main():
    """Main bot function with error handling and graceful shutdown"""
    # Setup logging
    logger = setup_logging()
    logger.info("="*60)
    logger.info("STARTING BOT APPLICATION")
    logger.info("="*60)
    
    # Setup signal handlers
    setup_signal_handlers()
    
    bot = None
    scheduler_service = None
    
    try:
        # Initialize Bot
        logger.info("Initializing bot...")
        bot = Bot(token=settings.BOT_TOKEN.get_secret_value())
        
        # Initialize Storage
        storage = MemoryStorage()
        logger.info("Memory storage initialized")

        dp = Dispatcher(storage=storage)

        # Register Middlewares
        logger.info("Registering middlewares...")
        # ChatTypeMiddleware as outer middleware to filter group messages before any processing
        dp.message.outer_middleware(ChatTypeMiddleware())
        dp.callback_query.outer_middleware(ChatTypeMiddleware())
        
        dp.update.middleware(UserMiddleware())
        dp.message.middleware(ErrorHandlingMiddleware()) # Global error handler
        dp.message.middleware(CheckStatusMiddleware())
        dp.callback_query.middleware(ErrorHandlingMiddleware()) # Global error handler
        dp.callback_query.middleware(CheckStatusMiddleware())

        # Register Routers
        logger.info("Registering handlers...")
        dp.include_router(registration.router)
        dp.include_router(user.router)
        dp.include_router(profile.router)
        dp.include_router(admin.router)

        # Initialize and start webinar scheduler
        logger.info("Starting webinar scheduler...")
        scheduler_service = WebinarSchedulerService(session_factory, bot)
        scheduler_service.start()
        
        # Startup actions
        await on_startup(bot)
        
        # Delete webhook and start polling
        logger.info("Deleting webhook...")
        await bot.delete_webhook(drop_pending_updates=True)
        
        logger.info("Starting polling...")
        logger.info("Bot is now running. Press Ctrl+C to stop.")
        
        # Start polling with error handling
        polling_task = asyncio.create_task(dp.start_polling(bot))
        shutdown_task = asyncio.create_task(shutdown_event.wait())
        
        # Wait for either polling to end or shutdown signal
        done, pending = await asyncio.wait(
            [polling_task, shutdown_task],
            return_when=asyncio.FIRST_COMPLETED
        )
        
        # Cancel pending tasks
        for task in pending:
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                pass
        
        logger.info("Bot stopped gracefully")
        
    except TelegramNetworkError as e:
        logger.error(f"Network error: {e}. Bot will restart automatically if configured.", exc_info=True)
        raise
        
    except TelegramRetryAfter as e:
        logger.error(f"Rate limited. Retry after {e.retry_after} seconds.", exc_info=True)
        await asyncio.sleep(e.retry_after)
        raise
        
    except Exception as e:
        logger.critical(f"Critical error in main(): {e}", exc_info=True)
        raise
        
    finally:
        logger.info("Executing cleanup...")
        await on_shutdown(bot, scheduler_service)
        logger.info("="*60)
        logger.info("BOT APPLICATION STOPPED")
        logger.info("="*60)


if __name__ == "__main__":
    exit_code = 0
    
    try:
        if sys.platform == "win32":
            asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
        
        asyncio.run(main())
        
    except KeyboardInterrupt:
        logging.info("Received keyboard interrupt")
        
    except SystemExit:
        logging.info("System exit")
        
    except Exception as e:
        logging.critical(f"Unhandled exception: {e}", exc_info=True)
        exit_code = 1
        
    finally:
        logging.info("Application terminated")
        sys.exit(exit_code)
