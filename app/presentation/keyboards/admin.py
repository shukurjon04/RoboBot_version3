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
