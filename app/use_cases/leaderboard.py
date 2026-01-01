
from typing import List, Tuple
from app.domain.repositories import AbstractUserRepository
from app.infrastructure.database.models import User

class LeaderboardService:
    def __init__(self, user_repo: AbstractUserRepository):
        self.user_repo = user_repo

    async def get_top_users(self, limit: int = 50) -> List[User]:
        return await self.user_repo.get_top_users_by_balance(limit)

    async def get_user_rank(self, user_id: int) -> int:
        return await self.user_repo.get_user_rank(user_id)
