from datetime import datetime
from typing import Optional
from sqlalchemy import BigInteger, String, Boolean, ForeignKey, DateTime, Integer, func, Identity
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.ext.asyncio import AsyncAttrs

from app.infrastructure.database.db_helper import Base
from app.domain.enums import UserStatus, ReferralStatus

class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=func.now(), onupdate=func.now())

class User(Base, AsyncAttrs, TimestampMixin):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    telegram_id: Mapped[int] = mapped_column(BigInteger, unique=True, autoincrement=False)

    username: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    first_name: Mapped[str] = mapped_column(String)
    full_name: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    phone_number: Mapped[Optional[str]] = mapped_column(String, nullable=True)  # Format: +998xxxxxxxxx
    phone_number_2: Mapped[Optional[str]] = mapped_column(String, nullable=True) # Secondary phone
    region: Mapped[Optional[str]] = mapped_column(String, nullable=True)  # Stores value from Region enum
    status: Mapped[UserStatus] = mapped_column(String, default=UserStatus.NEW)
    referrer_id: Mapped[Optional[int]] = mapped_column(BigInteger, ForeignKey("users.telegram_id"), nullable=True)
    balance: Mapped[int] = mapped_column(Integer, default=0)
    study_status: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    age_range: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    has_voucher: Mapped[bool] = mapped_column(Boolean, default=False)

    # Relationships
    referrals_made = relationship("Referral", back_populates="referrer", foreign_keys="Referral.referrer_id")
    survey_answer = relationship("UserSurveyAnswer", back_populates="user", uselist=False)
    point_history = relationship("PointHistory", back_populates="user")
    rewards = relationship("UserReward", back_populates="user")

class Channel(Base, AsyncAttrs, TimestampMixin):
    __tablename__ = "channels"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    channel_id: Mapped[str] = mapped_column(String, unique=True) # e.g. -100123456789
    name: Mapped[str] = mapped_column(String)
    link: Mapped[str] = mapped_column(String)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

class UserSurveyAnswer(Base, AsyncAttrs, TimestampMixin):
    __tablename__ = "user_survey_answers"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.telegram_id"), unique=True)
    answer: Mapped[str] = mapped_column(String)

    user = relationship("User", back_populates="survey_answer")

class Referral(Base, AsyncAttrs, TimestampMixin):
    __tablename__ = "referrals"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    referrer_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.telegram_id"))
    referred_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.telegram_id"), unique=True)
    status: Mapped[ReferralStatus] = mapped_column(String, default=ReferralStatus.PENDING)

    referrer = relationship("User", foreign_keys=[referrer_id], back_populates="referrals_made")
    # referred user relationship can be added if needed

class PointHistory(Base, AsyncAttrs, TimestampMixin):
    __tablename__ = "point_history"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.telegram_id"))
    amount: Mapped[int] = mapped_column(Integer)
    reason: Mapped[str] = mapped_column(String)

    user = relationship("User", back_populates="point_history")

class Reward(Base, AsyncAttrs, TimestampMixin):
    __tablename__ = "rewards"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String)
    description: Mapped[str] = mapped_column(String)
    cost: Mapped[int] = mapped_column(Integer)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

class UserReward(Base, AsyncAttrs, TimestampMixin):
    __tablename__ = "user_rewards"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.telegram_id"))
    reward_id: Mapped[int] = mapped_column(Integer, ForeignKey("rewards.id"))
    
    user = relationship("User", back_populates="rewards")
    reward = relationship("Reward")

class Admin(Base, AsyncAttrs, TimestampMixin):
    __tablename__ = "admins"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    telegram_id: Mapped[int] = mapped_column(BigInteger, unique=True)
    description: Mapped[Optional[str]] = mapped_column(String, nullable=True)

class WebinarSettings(Base, AsyncAttrs, TimestampMixin):
    __tablename__ = "webinar_settings"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    webinar_datetime: Mapped[datetime] = mapped_column(DateTime)
    webinar_link: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    
    sent_1h: Mapped[bool] = mapped_column(Boolean, default=False)
    sent_30m: Mapped[bool] = mapped_column(Boolean, default=False)
    sent_15m: Mapped[bool] = mapped_column(Boolean, default=False)
    sent_5m: Mapped[bool] = mapped_column(Boolean, default=False)
    sent_start: Mapped[bool] = mapped_column(Boolean, default=False)
