import asyncio
from sqlalchemy import select
from app.infrastructure.database.db_helper import session_factory
from app.infrastructure.database.models import Channel

async def dump_channels():
    async with session_factory() as session:
        stmt = select(Channel)
        result = await session.execute(stmt)
        channels = result.scalars().all()
        print(f"Total channels: {len(channels)}")
        for ch in channels:
            print(f"ID: {ch.id}, TG_ID: {ch.channel_id}, Name: {ch.name}, Link: {ch.link}, Active: {ch.is_active}")

if __name__ == "__main__":
    asyncio.run(dump_channels())
