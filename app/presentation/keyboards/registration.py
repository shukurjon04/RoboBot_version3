from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
from app.domain.enums import Region, StudyStatus, AgeRange
from app.infrastructure.database.models import Channel
from typing import List

def check_subscription_kb(channels: List[Channel]) -> InlineKeyboardMarkup:
    keyboard = []
    for ch in channels:
        keyboard.append([InlineKeyboardButton(text=f"➕ {ch.name}", url=ch.link)])
    
    keyboard.append([InlineKeyboardButton(text="Tasdiqlash ✅", callback_data="check_subscription")])
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

def phone_kb() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(keyboard=[
        [KeyboardButton(text="📞 Kontaktingizni yuboring", request_contact=True)],
        [KeyboardButton(text="⬅️ Bekor qilish")]
    ], resize_keyboard=True, one_time_keyboard=True)

def regions_kb() -> InlineKeyboardMarkup:
    # 2 columns
    keyboard = []
    row = []
    for region in Region:
        row.append(InlineKeyboardButton(text=region.value, callback_data=f"region:{region.value}"))
        if len(row) == 2:
            keyboard.append(row)
            row = []
    if row:
        keyboard.append(row)
    keyboard.append([InlineKeyboardButton(text="⬅️ Orqaga", callback_data="back_to_fields")])
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

def study_status_kb() -> InlineKeyboardMarkup:
    keyboard = [
        [InlineKeyboardButton(text=StudyStatus.TWO_MONTHS.value, callback_data=f"study:{StudyStatus.TWO_MONTHS.name}")],
        [InlineKeyboardButton(text=StudyStatus.FIVE_MONTHS.value, callback_data=f"study:{StudyStatus.FIVE_MONTHS.name}")],
        [InlineKeyboardButton(text=StudyStatus.NO.value, callback_data=f"study:{StudyStatus.NO.name}")],
        [InlineKeyboardButton(text=StudyStatus.OTHER.value, callback_data=f"study:{StudyStatus.OTHER.name}")],
        [InlineKeyboardButton(text="⬅️ Orqaga", callback_data="back_to_fields")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

def age_range_kb() -> InlineKeyboardMarkup:
    keyboard = []
    # 1 column for aged range to be clear
    for age in AgeRange:
        keyboard.append([InlineKeyboardButton(text=age.value, callback_data=f"age:{age.name}")])
    keyboard.append([InlineKeyboardButton(text="⬅️ Orqaga", callback_data="back_to_fields")])
    return InlineKeyboardMarkup(inline_keyboard=keyboard)
