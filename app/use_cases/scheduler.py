from datetime import datetime
from typing import Optional
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
import logging

from app.domain.repositories import AbstractUserRepository
from app.infrastructure.database.models import WebinarSettings
from app.utils.formatters import format_uzb_time
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from aiogram import Bot

logger = logging.getLogger(__name__)

class WebinarSchedulerService:
    def __init__(self, session_factory, bot: Bot, user_repo: AbstractUserRepository):
        self.session_factory = session_factory
        self.bot = bot
        self.user_repo = user_repo
        self.scheduler = AsyncIOScheduler()
        
    async def check_and_send_reminder(self):
        """Check if webinar is approaching and send appropriate reminders"""
        try:
            async with self.session_factory() as session:
                # Get the latest webinar settings
                stmt = select(WebinarSettings).order_by(WebinarSettings.created_at.desc()).limit(1)
                result = await session.execute(stmt)
                webinar = result.scalar_one_or_none()
                
                if not webinar:
                    return
                    
                now = datetime.now()
                # Time until webinar in minutes
                time_until = (webinar.webinar_datetime - now).total_seconds() / 60
                
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
                    logger.info(f"Checking {target_reminder['flag']} for webinar at {webinar.webinar_datetime}")
                    
                    users = await self.user_repo.get_all_users()
                    
                    # Format the webinar time for the message
                    webinar_time_str = format_uzb_time(webinar.webinar_datetime)
                    
                    message = (
                        "🎁 <b>Siz yutishga tayyormisiz?</b>\n\n"
                        f"{target_reminder['msg']}\n"
                        f"⏰ Vebinar boshlanish vaqti: <b>{webinar_time_str}</b>\n\n"
                        "Reyting g'oliblarini aniqlaymiz! 🏆\n\n"
                        f"👉 <b>Vebinarga qo'shilish:</b> {webinar.webinar_link}\n\n"
                        "Tayyor turing!"
                    )
                    
                    sent_count = 0
                    logger.info(f"Starting broadcast for {target_reminder['flag']} to {len(users)} users...")
                    for user in users:
                        try:
                            await self.bot.send_message(
                                chat_id=user.telegram_id,
                                text=message,
                                parse_mode="HTML"
                            )
                            sent_count += 1
                        except Exception as e:
                            # Log individual failures but continue the broadcast
                            pass
                    
                    # Mark this specific reminder as sent
                    setattr(webinar, target_reminder["flag"], True)
                    await session.commit()
                    logger.info(f"Successfully sent {target_reminder['flag']} to {sent_count}/{len(users)} users")
                    
        except Exception as e:
            logger.error(f"Error in check_and_send_reminder: {e}", exc_info=True)
    
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
        logger.info("Webinar scheduler started (checking every 10 minutes)")
    
    def shutdown(self):
        """Shutdown the scheduler"""
        if self.scheduler.running:
            self.scheduler.shutdown()
            logger.info("Webinar scheduler shut down")
