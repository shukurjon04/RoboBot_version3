
import asyncio
from app.infrastructure.database.db_helper import session_factory
from sqlalchemy import text

async def check_tables():
    async with session_factory() as session:
        result = await session.execute(text("SELECT table_name FROM information_schema.tables WHERE table_schema='public'"))
        tables = result.scalars().all()
        print(f"Tables in DB: {tables}")

if __name__ == "__main__":
    asyncio.run(check_tables())
