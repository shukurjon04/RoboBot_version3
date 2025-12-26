from app.domain.repositories import AbstractReferralRepository, AbstractUserRepository

class ReferralService:
    def __init__(self, referral_repo: AbstractReferralRepository, user_repo: AbstractUserRepository):
        self.referral_repo = referral_repo
        self.user_repo = user_repo

    async def get_referral_stats(self, user_id: int) -> dict:
        count = await self.referral_repo.get_referral_count(user_id)
        user = await self.user_repo.get_user(user_id)
        return {
            "count": count,
            "points": user.balance
        }

    def get_referral_link(self, bot_username: str, user_id: int) -> str:
        return f"https://t.me/{bot_username}?start={user_id}"
