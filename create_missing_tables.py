
import asyncio
import logging
from app.infrastructure.database.db_helper import engine, Base
from app.infrastructure.database.models import * # Import all models to register them with Base

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def create_tables():
    logger.info("Ensuring all tables exist...")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("Tables checked and created if missing.")
    await engine.dispose()

if __name__ == "__main__":
    asyncio.run(create_tables())
