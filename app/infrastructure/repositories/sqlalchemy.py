from typing import Optional, List
from sqlalchemy import select, update, delete, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.domain.repositories import (
    AbstractUserRepository, 
    AbstractChannelRepository, 
    AbstractSurveyRepository, 
    AbstractReferralRepository
)
from app.infrastructure.database.models import (
    User, Channel, UserSurveyAnswer, Referral, PointHistory, UserStatus, ReferralStatus
)

class SQLAlchemyUserRepository(AbstractUserRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_user(self, telegram_id: int) -> Optional[User]:
        stmt = select(User).where(User.telegram_id == telegram_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_user_by_phone(self, phone_number: str) -> Optional[User]:
        stmt = select(User).where(User.phone_number == phone_number)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def create_user(self, telegram_id: int, first_name: str, username: Optional[str], referrer_id: Optional[int] = None) -> User:
        user = User(
            telegram_id=telegram_id,
            first_name=first_name,
            username=username,
            referrer_id=referrer_id,
            status=UserStatus.NEW  # Explicitly NEW
        )
        self.session.add(user)
        await self.session.commit()
        await self.session.refresh(user)
        return user

    async def update_status(self, telegram_id: int, status: UserStatus) -> User:
        stmt = update(User).where(User.telegram_id == telegram_id).values(status=status).returning(User)
        result = await self.session.execute(stmt)
        await self.session.commit()
        return result.scalar_one()

    async def add_points(self, telegram_id: int, amount: int, reason: str) -> User:
        # Add history
        history = PointHistory(user_id=telegram_id, amount=amount, reason=reason)
        self.session.add(history)
        
        # Update balance
        stmt = update(User).where(User.telegram_id == telegram_id).values(balance=User.balance + amount).returning(User)
        result = await self.session.execute(stmt)
        await self.session.commit()
        return result.scalar_one()

    async def get_all_users(self) -> List[User]:
        stmt = select(User)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_top_users_by_balance(self, limit: int) -> List[User]:
        stmt = select(User).order_by(User.balance.desc()).limit(limit)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_user_rank(self, telegram_id: int) -> int:
        # Rank is count of users with more balance + 1
        # Providing a simple rank logic. For dense rank or others, complex query needed.
        # This is basic row number equivalent.
        user_balance_stmt = select(User.balance).where(User.telegram_id == telegram_id)
        user_balance = await self.session.scalar(user_balance_stmt)
        
        if user_balance is None:
            return 0
            
        stmt = select(func.count()).select_from(User).where(User.balance > user_balance)
        count_submission = await self.session.scalar(stmt)
        return count_submission + 1

    async def update_profile(
        self, 
        telegram_id: int, 
        full_name: Optional[str] = None, 
        phone_number: Optional[str] = None, 
        region: Optional[str] = None,
        study_status: Optional[str] = None,
        age_range: Optional[str] = None,
        phone_number_2: Optional[str] = None
    ) -> User:
        values = {}
        if full_name:
            values['full_name'] = full_name
        if phone_number:
            values['phone_number'] = phone_number
        if region:
            values['region'] = region
        if study_status:
            values['study_status'] = study_status
        if age_range:
            values['age_range'] = age_range
        if phone_number_2:
            values['phone_number_2'] = phone_number_2
            
        if not values:
             return await self.get_user(telegram_id)

        stmt = update(User).where(User.telegram_id == telegram_id).values(**values).returning(User)
        result = await self.session.execute(stmt)
        await self.session.commit()
        return result.scalar_one()

class SQLAlchemyChannelRepository(AbstractChannelRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_all_active(self) -> List[Channel]:
        stmt = select(Channel).where(Channel.is_active == True)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_all(self) -> List[Channel]:
        stmt = select(Channel)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def add_channel(self, channel_id: str, name: str, link: str) -> Channel:
        channel = Channel(channel_id=channel_id, name=name, link=link)
        self.session.add(channel)
        await self.session.commit()
        return channel

    async def delete_channel(self, id: int) -> None:
        stmt = delete(Channel).where(Channel.id == id)
        await self.session.execute(stmt)
        await self.session.commit()

class SQLAlchemySurveyRepository(AbstractSurveyRepository):
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def save_answer(self, user_id: int, answer: str) -> UserSurveyAnswer:
        survey = UserSurveyAnswer(user_id=user_id, answer=answer)
        self.session.add(survey)
        await self.session.commit()
        return survey

class SQLAlchemyReferralRepository(AbstractReferralRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_referral(self, referrer_id: int, referred_id: int) -> None:
        referral = Referral(referrer_id=referrer_id, referred_id=referred_id, status=ReferralStatus.PENDING)
        self.session.add(referral)
        await self.session.commit()

    async def confirm_referral(self, referrer_id: int, referred_id: int) -> None:
        stmt = update(Referral).where(
            Referral.referrer_id == referrer_id, 
            Referral.referred_id == referred_id
        ).values(status=ReferralStatus.CONFIRMED)
        await self.session.execute(stmt)
        await self.session.commit()

    async def get_referral_count(self, user_id: int) -> int:
        stmt = select(func.count()).select_from(Referral).where(
            Referral.referrer_id == user_id, 
            Referral.status == ReferralStatus.CONFIRMED
        )
        result = await self.session.execute(stmt)
        return result.scalar()
