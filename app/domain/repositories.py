from abc import ABC, abstractmethod
from typing import Optional, List
from app.infrastructure.database.models import User, Channel, UserSurveyAnswer, UserStatus, ReferralStatus

class AbstractUserRepository(ABC):
    @abstractmethod
    async def get_user(self, telegram_id: int) -> Optional[User]:
        pass

    @abstractmethod
    async def get_user_by_phone(self, phone_number: str) -> Optional[User]:
        pass

    @abstractmethod
    async def create_user(self, telegram_id: int, first_name: str, username: Optional[str], referrer_id: Optional[int] = None) -> User:
        pass

    @abstractmethod
    async def update_status(self, telegram_id: int, status: UserStatus) -> User:
        pass

    @abstractmethod
    async def add_points(self, telegram_id: int, amount: int, reason: str) -> User:
        pass

    @abstractmethod
    async def get_all_users(self) -> List[User]:
        pass

    @abstractmethod
    async def get_top_users_by_balance(self, limit: int) -> List[User]:
        pass

    @abstractmethod
    async def get_user_rank(self, telegram_id: int) -> int:
        pass

    @abstractmethod
    async def update_profile(
        self, 
        telegram_id: int, 
        full_name: Optional[str] = None, 
        phone_number: Optional[str] = None, 
        region: Optional[str] = None,
        study_status: Optional[str] = None,
        age_range: Optional[str] = None,
        phone_number_2: Optional[str] = None,
        has_voucher: Optional[bool] = None
    ) -> User:
        pass

class AbstractChannelRepository(ABC):
    @abstractmethod
    async def get_all_active(self) -> List[Channel]:
        pass
    
    @abstractmethod
    async def get_all(self) -> List[Channel]:
        pass

    @abstractmethod
    async def add_channel(self, channel_id: str, name: str, link: str) -> Channel:
        pass

    @abstractmethod
    async def delete_channel(self, id: int) -> None:
        pass

class AbstractSurveyRepository(ABC):
    @abstractmethod
    async def save_answer(self, user_id: int, answer: str) -> UserSurveyAnswer:
        pass

class AbstractReferralRepository(ABC):
    @abstractmethod
    async def create_referral(self, referrer_id: int, referred_id: int) -> None:
        pass

    @abstractmethod
    async def confirm_referral(self, referrer_id: int, referred_id: int) -> None:
        pass

    @abstractmethod
    async def get_referral_count(self, user_id: int) -> int:
        pass
