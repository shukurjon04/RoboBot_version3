from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from app.infrastructure.database.models import Channel
from typing import List

def channels_list_kb(channels: List[Channel]) -> InlineKeyboardMarkup:
    keyboard = []
    for ch in channels:
        keyboard.append([
            InlineKeyboardButton(text=f"❌ {ch.name}", callback_data=f"del_channel:{ch.id}")
        ])
    keyboard.append([InlineKeyboardButton(text="➕ Yangi kanal qo'shish", callback_data="add_channel")])
    keyboard.append([InlineKeyboardButton(text="⬅️ Orqaga", callback_data="back_to_admin_main")])
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

def back_to_channels_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="⬅️ Orqaga", callback_data="back_to_channels_list")]
    ])
