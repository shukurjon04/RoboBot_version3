import asyncio
from sqlalchemy import select
from app.infrastructure.database.db_helper import session_factory
from app.infrastructure.database.models import WebinarCheckin, User

async def debug_db():
    async with session_factory() as session:
        print("--- Last 10 Webinar Checkins ---")
        stmt = select(WebinarCheckin).order_by(WebinarCheckin.id.desc()).limit(10)
        result = await session.execute(stmt)
        checkins = result.scalars().all()
        for c in checkins:
            print(f"ID: {c.id}, UserID (FK): {c.user_id}, CheckedAt: {c.checked_at}")
        
        print("\n--- Last 5 Users ---")
        stmt = select(User).order_by(User.id.desc()).limit(5)
        result = await session.execute(stmt)
        users = result.scalars().all()
        for u in users:
            print(f"ID: {u.id}, TelegramID: {u.telegram_id}, Name: {u.full_name or u.first_name}")

if __name__ == "__main__":
    asyncio.run(debug_db())
