from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def profile_menu_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📝 Ma'lumotlarni tahrirlash", callback_data="edit_profile")],
        [InlineKeyboardButton(text="⬅️ Orqaga", callback_data="back_to_main")]
    ])

def edit_fields_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="👤 Ism-familiya", callback_data="edit_field:full_name")],
        [InlineKeyboardButton(text="📞 Telefon raqami", callback_data="edit_field:phone_number")],
        [InlineKeyboardButton(text="📍 Hudud", callback_data="edit_field:region")],
        [InlineKeyboardButton(text="🎓 O'quv holati", callback_data="edit_field:study_status")],
        [InlineKeyboardButton(text="⏳ Yosh toifasi", callback_data="edit_field:age_range")],
        [InlineKeyboardButton(text="⬅️ Orqaga", callback_data="back_to_profile")]
    ])

def phone_edit_options_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📞 Hozirgini tahrirlash", callback_data="phone_opt:edit_current")],
        [InlineKeyboardButton(text="➕ Ikkinchi raqam qo'shish", callback_data="phone_opt:add_second")],
        [InlineKeyboardButton(text="⬅️ Orqaga", callback_data="back_to_fields")]
    ])
