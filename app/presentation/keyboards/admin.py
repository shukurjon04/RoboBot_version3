from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

admin_kb = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="📢 Rassilka"),
            KeyboardButton(text="📊 Reyting Excel")
        ],
        [
            KeyboardButton(text="⚠️ Shubhali foydalanuvchilar"),
            KeyboardButton(text="⏰ Vebinar vaqti")
        ],
        [
            KeyboardButton(text="📢 Kanallarni boshqarish"),
            KeyboardButton(text="✅ Check-in")
        ],
        [
            KeyboardButton(text="📥 Vebinar qatnashchilari"),
            KeyboardButton(text="🏠 Asosiy menyu")
        ],
        [
            KeyboardButton(text="💾 Bazani yuklash"),
            KeyboardButton(text="♻️ Bazani tiklash")
        ]
    ],
    resize_keyboard=True
)

def admin_back_kb() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="⬅️ Orqaga")]],
        resize_keyboard=True
    )

def suspicious_users_kb():
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="✉️ Barchasiga xabar yuborish", callback_data="send_to_suspicious")]
        ]
    )

def checkin_button_kb(bot_username: str):
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="✅ Men shu yerdaman", url=f"https://t.me/{bot_username}?start=checkin")]
        ]
    )
