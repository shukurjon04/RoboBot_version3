from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

def main_menu_kb() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(keyboard=[
        [KeyboardButton(text="➕ Ball yig‘ish"), KeyboardButton(text="💰 Ballarim")],
        [KeyboardButton(text="👤 Profil"), KeyboardButton(text="📊 Reyting (TOP-50)")],
        [KeyboardButton(text="🎁 Sovg‘alar va Shartlar"), KeyboardButton(text="🎓 Kurslar haqida")],
        [KeyboardButton(text="📞 Bog‘lanish")]
    ], resize_keyboard=True)
