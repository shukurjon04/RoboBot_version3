
import asyncio
from app.infrastructure.database.db_helper import session_factory
from sqlalchemy import text

async def check_tables():
    from app.infrastructure.database.db_helper import engine
    try:
        async with session_factory() as session:
            # SQLite specific way to get table names
            result = await session.execute(text("SELECT name FROM sqlite_master WHERE type='table'"))
            tables = result.scalars().all()
            print(f"Tables in DB: {tables}", flush=True)
    finally:
        await engine.dispose()

if __name__ == "__main__":
    asyncio.run(check_tables())
