from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import DeclarativeBase

from app.config.settings import settings

class Base(DeclarativeBase):
    pass

engine = create_async_engine(
    url=settings.database_url,
    echo=False,
)

session_factory = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False
)

async def get_db_session() -> AsyncSession:
    async with session_factory() as session:
        yield session
