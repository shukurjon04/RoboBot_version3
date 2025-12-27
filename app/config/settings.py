from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import SecretStr
from typing import List

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file='.env', env_ignore_empty=True, extra='ignore')

    BOT_TOKEN: SecretStr
    ADMIN_IDS: List[int]
    
    @property
    def database_url(self) -> str:
        return f"sqlite+aiosqlite:///./data/bot_v2.sqlite3"

settings = Settings()
