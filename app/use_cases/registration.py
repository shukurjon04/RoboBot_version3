from typing import Optional
from app.domain.repositories import AbstractUserRepository, AbstractReferralRepository
from app.domain.enums import UserStatus, ReferralStatus

class RegistrationService:
    def __init__(self, user_repo: AbstractUserRepository, referral_repo: AbstractReferralRepository):
        self.user_repo = user_repo
        self.referral_repo = referral_repo

    async def register_user(self, telegram_id: int, first_name: str, username: Optional[str], referrer_id: Optional[int] = None):
        user = await self.user_repo.get_user(telegram_id)
        if user:
            return user
        
        # Determine valid referrer
        valid_referrer = None
        if referrer_id and referrer_id != telegram_id:
            referrer = await self.user_repo.get_user(referrer_id)
            if referrer:
                valid_referrer = referrer_id

        # Create new user
        user = await self.user_repo.create_user(telegram_id, first_name, username, valid_referrer)
        
        # If referred, create pending referral record
        if valid_referrer:
            await self.referral_repo.create_referral(valid_referrer, telegram_id)

        return user

    async def update_user_profile(
        self, 
        telegram_id: int, 
        full_name: Optional[str] = None, 
        phone_number: Optional[str] = None, 
        region: Optional[str] = None,
        study_status: Optional[str] = None,
        age_range: Optional[str] = None
    ):
        await self.user_repo.update_profile(telegram_id, full_name, phone_number, region, study_status, age_range)

    async def complete_registration_step_channels(self, telegram_id: int):
        await self.user_repo.update_status(telegram_id, UserStatus.WAIT_SURVEY)

    async def complete_registration(self, telegram_id: int):
        # Finalize user status
        await self.user_repo.update_status(telegram_id, UserStatus.ACTIVE)
        
        # Add welcome bonus to user (if any rules exist) - optional
        await self.user_repo.add_points(telegram_id, 10, "Registration Bonus")

        # Process referral reward
        user = await self.user_repo.get_user(telegram_id)
        if user.referrer_id:
             await self.referral_repo.confirm_referral(user.referrer_id, telegram_id)
             # Add points to referrer
             await self.user_repo.add_points(user.referrer_id, 10, f"Referral: {user.first_name}")
             return user.referrer_id
        
        return None
