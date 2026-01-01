import asyncio
import sys
from sqlalchemy import select
from app.infrastructure.database.db_helper import session_factory
from app.infrastructure.database.models import WebinarSettings
from datetime import datetime

async def main():
    async with session_factory() as session:
        stmt = select(WebinarSettings).order_by(WebinarSettings.created_at.desc()).limit(1)
        result = await session.execute(stmt)
        webinar = result.scalar_one_or_none()
        
        if webinar:
            print(f"ID: {webinar.id}")
            print(f"Webinar Datetime: {webinar.webinar_datetime}")
            print(f"Current System Time: {datetime.now()}")
            print(f"Time Until (minutes): {(webinar.webinar_datetime - datetime.now()).total_seconds() / 60}")
            print(f"Link: {webinar.webinar_link}")
            print(f"Sent 1h: {webinar.sent_1h}")
            print(f"Sent 30m: {webinar.sent_30m}")
            print(f"Sent 15m: {webinar.sent_15m}")
            print(f"Sent 5m: {webinar.sent_5m}")
            print(f"Sent Start: {webinar.sent_start}")
        else:
            print("No webinar settings found.")

if __name__ == "__main__":
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(main())
