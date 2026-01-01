from aiogram.fsm.storage.redis import RedisStorage
from redis.asyncio import Redis
from app.config.settings import settings

def make_redis_storage() -> RedisStorage:
    redis = Redis.from_url(settings.redis_url)
    return RedisStorage(redis=redis)
