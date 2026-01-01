from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from datetime import datetime
import calendar

def webinar_years_kb() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    current_year = datetime.now().year
    for year in range(current_year, current_year + 6):
        builder.button(text=str(year), callback_data=f"wb_year:{year}")
    builder.adjust(1)
    builder.row(InlineKeyboardButton(text="⬅️ Orqaga", callback_data="wb_back_to_admin"))
    return builder.as_markup()

def webinar_months_kb() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    months = [
        "Yanvar", "Fevral", "Mart", "Aprel", "May", "Iyun",
        "Iyul", "Avgust", "Sentabr", "Oktabr", "Noyabr", "Dekabr"
    ]
    for i, month in enumerate(months, 1):
        builder.button(text=month, callback_data=f"wb_month:{i:02d}")
    builder.adjust(3)
    # Add back button via callback if needed, but here we might prefer FSM back
    builder.row(InlineKeyboardButton(text="⬅️ Orqaga", callback_data="wb_back_to_year"))
    return builder.as_markup()

def webinar_days_kb(year: int, month: int) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    _, last_day = calendar.monthrange(year, month)
    
    for day in range(1, last_day + 1):
        builder.button(text=str(day), callback_data=f"wb_day:{day:02d}")
    
    builder.adjust(7)
    builder.row(InlineKeyboardButton(text="⬅️ Orqaga", callback_data="wb_back_to_month"))
    return builder.as_markup()

def webinar_hours_kb() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for hour in range(24):
        builder.button(text=f"{hour:02d}:00", callback_data=f"wb_hour:{hour:02d}")
    builder.adjust(4)
    builder.row(InlineKeyboardButton(text="⬅️ Orqaga", callback_data="wb_back_to_day"))
    return builder.as_markup()

def webinar_minutes_kb(hour: str) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for minute in range(0, 60, 5):
        builder.button(text=f"{hour}:{minute:02d}", callback_data=f"wb_minute:{minute:02d}")
    builder.adjust(4)
    builder.row(InlineKeyboardButton(text="⬅️ Orqaga", callback_data="wb_back_to_hour"))
    return builder.as_markup()
