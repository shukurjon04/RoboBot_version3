import asyncio
from datetime import datetime
from typing import Optional, List
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
import logging

from app.domain.repositories import AbstractUserRepository
from app.infrastructure.database.models import WebinarSettings, User
from app.utils.formatters import format_uzb_time
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from aiogram import Bot
from aiogram.exceptions import TelegramRetryAfter, TelegramForbiddenError
from app.config.settings import settings
from app.infrastructure.repositories.sqlalchemy import SQLAlchemyUserRepository

logger = logging.getLogger(__name__)

class WebinarSchedulerService:
    def __init__(self, session_factory, bot: Bot):
        self.session_factory = session_factory
        self.bot = bot
        self.scheduler = AsyncIOScheduler()
        # Limit concurrent sends to avoid flood limits (20 msgs/sec is safer)
        self.semaphore = asyncio.Semaphore(20)
        
    async def check_and_send_reminder(self):
        """Check if webinar is approaching and trigger reminders"""
        try:
            async with self.session_factory() as session:
                # Get the latest webinar settings
                stmt = select(WebinarSettings).order_by(WebinarSettings.created_at.desc()).limit(1)
                result = await session.execute(stmt)
                webinar = result.scalar_one_or_none()
                
                if not webinar:
                    return
                    
                now = datetime.now()
                # TZ is set to Asia/Tashkent in Docker, so datetime.now() is already correct
                
                # Time until webinar in minutes
                time_until = (webinar.webinar_datetime - now).total_seconds() / 60
                
                # Log timing for debugging (only at DEBUG level to avoid log bloat)
                logger.debug(f"Webinar check: now={now}, webinar={webinar.webinar_datetime}, until={time_until:.1f}m")
                
                reminders = [
                    {"threshold": 60, "flag": "sent_1h", "msg": "Vebinar 1 soatdan keyin boshlanadi! ⏰"},
                    {"threshold": 30, "flag": "sent_30m", "msg": "Vebinar boshlanishiga 30 daqiqa qoldi! ⏳"},
                    {"threshold": 15, "flag": "sent_15m", "msg": "Vebinar boshlanishiga 15 daqiqa qoldi! 🔔"},
                    {"threshold": 5, "flag": "sent_5m", "msg": "Vebinar 5 daqiqadan so'ng boshlanadi! 🚀"},
                    {"threshold": 0, "flag": "sent_start", "msg": "Vebinar boshlandi! Tezroq qo'shiling! 🔥"}
                ]

                target_reminder = None
                for r in reminders:
                    # If we are within 2 minutes of the threshold and haven't sent it yet
                    # For threshold 0, we check if 0 >= time_until >= -30 (don't send if more than 30m late)
                    if r["threshold"] == 0:
                        if 0 >= time_until >= -30 and not getattr(webinar, r["flag"]):
                            target_reminder = r
                            break
                    elif r["threshold"] - 2 <= time_until <= r["threshold"] and not getattr(webinar, r["flag"]):
                        target_reminder = r
                        break

                if target_reminder:
                    logger.info(f"Triggering {target_reminder['flag']} for webinar at {webinar.webinar_datetime}")
                    
                    user_repo = SQLAlchemyUserRepository(session)
                    users = await user_repo.get_all_users()
                    
                    # Mark this specific reminder as sent IMMEDIATELY to prevent double triggering
                    setattr(webinar, target_reminder["flag"], True)
                    await session.commit()
                    
                    # Run broadcast in background so it doesn't block the scheduler
                    asyncio.create_task(self._run_broadcast(users, target_reminder, webinar))
                    
        except Exception as e:
            logger.error(f"Error in check_and_send_reminder: {e}", exc_info=True)

    async def _run_broadcast(self, users: List[User], reminder: dict, webinar: WebinarSettings):
        """Perform non-blocking broadcast with rate limiting"""
        sent_count = 0
        blocked_count = 0
        error_count = 0
        admin_ids = set(settings.ADMIN_IDS)
        
        webinar_time_str = format_uzb_time(webinar.webinar_datetime)
        message = (
            "🎁 <b>Siz yutishga tayyormisiz?</b>\n\n"
            # f"{reminder['msg']}\n"
            f"⏰ Vebinar boshlanish vaqti: <b>{webinar_time_str}</b>\n\n"
            "Reyting g'oliblarini aniqlaymiz! 🏆\n\n"
            f"👉 <b>Vebinarga qo'shilish:</b> {webinar.webinar_link}\n\n"
            "Tayyor turing!"
        )

        async def send_to_user(user: User):
            nonlocal sent_count, blocked_count, error_count
            if user.telegram_id in admin_ids:
                return

            async with self.semaphore:
                try:
                    await self.bot.send_message(
                        chat_id=user.telegram_id,
                        text=message,
                        parse_mode="HTML"
                    )
                    sent_count += 1
                except TelegramForbiddenError:
                    blocked_count += 1
                except TelegramRetryAfter as e:
                    logger.warning(f"Rate limited! Sleeping for {e.retry_after}s")
                    await asyncio.sleep(e.retry_after)
                    # Retry once
                    try:
                        await self.bot.send_message(chat_id=user.telegram_id, text=message, parse_mode="HTML")
                        sent_count += 1
                    except Exception:
                        error_count += 1
                except Exception as e:
                    error_count += 1
                    logger.debug(f"Failed to send to {user.telegram_id}: {e}")

        logger.info(f"Starting broadcast tasks for {reminder['flag']} to {len(users)} users...")
        tasks = [send_to_user(user) for user in users]
        await asyncio.gather(*tasks)
        
        logger.info(
            f"Finish {reminder['flag']} broadcast: "
            f"Sent: {sent_count}, Blocked: {blocked_count}, Errors: {error_count}"
        )
    
    def start(self):
        """Start the scheduler with 1-minute interval checks"""
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        logger.info(f"Starting webinar scheduler. Bot local time: {current_time} (Timezone: Asia/Tashkent)")
        
        self.scheduler.add_job(
            self.check_and_send_reminder,
            trigger=IntervalTrigger(minutes=1),
            id='webinar_reminder_check',
            replace_existing=True
        )
        self.scheduler.start()
        logger.info("Webinar scheduler started (checking every 1 minute)")
    
    def shutdown(self):
        """Shutdown the scheduler"""
        if self.scheduler.running:
            self.scheduler.shutdown()
            logger.info("Webinar scheduler shut down")
