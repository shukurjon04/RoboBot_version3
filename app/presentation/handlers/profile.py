from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, ReplyKeyboardRemove, ReplyKeyboardMarkup, KeyboardButton
from aiogram.fsm.context import FSMContext

from app.domain.repositories import AbstractUserRepository, AbstractReferralRepository
from app.domain.enums import StudyStatus, AgeRange
from app.presentation.keyboards.profile import profile_menu_kb, edit_fields_kb, phone_edit_options_kb
from app.presentation.keyboards.registration import regions_kb, phone_kb, study_status_kb, age_range_kb
from app.presentation.keyboards.main import main_menu_kb
from app.presentation.states import ProfileSG

router = Router()

@router.message(F.text == "👤 Profil")
async def show_profile(message: Message, db_user, referral_repo: AbstractReferralRepository, state: FSMContext):
    await state.clear()

    if not db_user:
        await message.answer("Siz ro'yxatdan o'tmagansiz, avval /start buyrug'i bilan ro'yxatdan o'ting.")
        return
    count = await referral_repo.get_referral_count(db_user.telegram_id)
    
    text = (
        "👤 <b>Sizning profilingiz:</b>\n\n"
        f"🆔 ID: <b>{db_user.id}</b>\n"
        f"👤 Ism-familiya: <b>{db_user.full_name or db_user.first_name}</b>\n"
        f"📞 Telefon: <b>{db_user.phone_number or 'Kiritilmagan'}</b>\n"
        f"📞 Telefon 2: <b>{db_user.phone_number_2 or 'Kiritilmagan'}</b>\n"
        f"📍 Hudud: <b>{db_user.region or 'Kiritilmagan'}</b>\n"
        f"🎓 Holat: <b>{db_user.study_status or 'Kiritilmagan'}</b>\n"
        f"⏳ Yosh: <b>{db_user.age_range or 'Kiritilmagan'}</b>\n\n"
        f"💰 Balans: <b>{db_user.balance} ball</b>\n"
        f"👥 Takliflar: <b>{count} ta</b>\n\n"
        "<i>Ma'lumotlaringizni tahrirlash uchun quyidagi tugmani bosing:</i>"
    )
    await message.answer(text, parse_mode="HTML", reply_markup=profile_menu_kb())
    await state.set_state(ProfileSG.main)

@router.callback_query(ProfileSG.main, F.data == "edit_profile")
async def on_edit_profile(callback: CallbackQuery):
    await callback.message.edit_text(
        "Qaysi ma'lumotni o'zgartirmoqchisiz?",
        reply_markup=edit_fields_kb()
    )

@router.callback_query(ProfileSG.main, F.data == "back_to_main")
async def on_back_to_main(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.delete()
    await callback.message.answer("Asosiy menyu:", reply_markup=main_menu_kb())

@router.callback_query(ProfileSG.main, F.data == "back_to_profile")
async def on_back_to_profile(callback: CallbackQuery, db_user, referral_repo: AbstractReferralRepository):
    count = await referral_repo.get_referral_count(db_user.telegram_id)
    text = (
        "👤 <b>Sizning profilingiz:</b>\n\n"
        f"🆔 ID: <b>{db_user.id}</b>\n"
        f"👤 Ism-familiya: <b>{db_user.full_name or db_user.first_name}</b>\n"
        f"📞 Telefon: <b>{db_user.phone_number or 'Kiritilmagan'}</b>\n"
        f"📞 Telefon 2: <b>{db_user.phone_number_2 or 'Kiritilmagan'}</b>\n"
        f"📍 Hudud: <b>{db_user.region or 'Kiritilmagan'}</b>\n"
        f"🎓 Holat: <b>{db_user.study_status or 'Kiritilmagan'}</b>\n"
        f"⏳ Yosh: <b>{db_user.age_range or 'Kiritilmagan'}</b>\n\n"
        f"💰 Balans: <b>{db_user.balance} ball</b>\n"
        f"👥 Takliflar: <b>{count} ta</b>"
    )
    await callback.message.edit_text(text, parse_mode="HTML", reply_markup=profile_menu_kb())

# Field Edit Entry Points
@router.callback_query(ProfileSG.main, F.data.startswith("edit_field:"))
async def on_edit_field_start(callback: CallbackQuery, state: FSMContext):
    field = callback.data.split(":")[1]
    
    if field == "full_name":
        await state.set_state(ProfileSG.edit_name)
        cancel_kb = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text="⬅️ Bekor qilish")]], resize_keyboard=True)
        await callback.message.answer("Ism familyani kiriting:", reply_markup=cancel_kb)
    elif field == "phone_number":
        await callback.message.edit_text("Telefon raqamini o'zgartirish yoki qo'shish:", reply_markup=phone_edit_options_kb())
    elif field == "region":
        await state.set_state(ProfileSG.edit_region)
        await callback.message.edit_text("Yangi hududni tanlang:", reply_markup=regions_kb())
    elif field == "study_status":
        await state.set_state(ProfileSG.edit_study_status)
        await callback.message.edit_text("O'quv holatingizni tanlang:", reply_markup=study_status_kb())
    elif field == "age_range":
        await state.set_state(ProfileSG.edit_age_range)
        await callback.message.edit_text("Yosh toifangizni tanlang:", reply_markup=age_range_kb())

# Field Update Handlers
@router.message(ProfileSG.edit_name, F.text)
async def update_name(message: Message, state: FSMContext, user_repo: AbstractUserRepository):
    await user_repo.update_profile(message.from_user.id, full_name=message.text)
    await message.answer("Ism-familiya yangilandi!", reply_markup=main_menu_kb())
    # Redirect to profile
    # Mocking call to show_profile or just send instructions
    await message.answer("Profilga qaytish uchun '👤 Profil' tugmasini bosing.")
    await state.clear()

@router.message(ProfileSG.edit_phone, F.contact)
@router.message(ProfileSG.edit_phone, F.text.regexp(r"^\+998\d{9}$"))
async def update_phone(message: Message, state: FSMContext, user_repo: AbstractUserRepository):
    phone = message.contact.phone_number if message.contact else message.text
    await user_repo.update_profile(message.from_user.id, phone_number=phone)
    await message.answer("Telefon raqami yangilandi!", reply_markup=main_menu_kb())
    await state.clear()

@router.message(ProfileSG.edit_phone_2, F.contact)
@router.message(ProfileSG.edit_phone_2, F.text.regexp(r"^\+998\d{9}$"))
async def update_phone_2(message: Message, state: FSMContext, user_repo: AbstractUserRepository):
    phone = message.contact.phone_number if message.contact else message.text
    await user_repo.update_profile(message.from_user.id, phone_number_2=phone)
    await message.answer("Ikkinchi telefon raqami saqlandi!", reply_markup=main_menu_kb())
    await state.clear()

@router.callback_query(F.data.startswith("phone_opt:"))
async def on_phone_option(callback: CallbackQuery, state: FSMContext):
    opt = callback.data.split(":")[1]
    if opt == "edit_current":
        await state.set_state(ProfileSG.edit_phone)
        await callback.message.answer("Yangi telefon raqamingizni yuboring:", reply_markup=phone_kb())
    elif opt == "add_second":
        await state.set_state(ProfileSG.edit_phone_2)
        await callback.message.answer("Ikkinchi telefon raqamini yuboring:", reply_markup=phone_kb())
    await callback.answer()

@router.callback_query(ProfileSG.edit_region, F.data.startswith("region:"))
async def update_region(callback: CallbackQuery, state: FSMContext, user_repo: AbstractUserRepository):
    region_val = callback.data.split(":", 1)[1]
    await user_repo.update_profile(callback.from_user.id, region=region_val)
    await callback.message.delete()
    await callback.message.answer("Hudud yangilandi!", reply_markup=main_menu_kb())
    await state.clear()

@router.callback_query(ProfileSG.edit_study_status, F.data.startswith("study:"))
async def update_study_status(callback: CallbackQuery, state: FSMContext, user_repo: AbstractUserRepository):
    study_val = callback.data.split(":", 1)[1]
    await user_repo.update_profile(callback.from_user.id, study_status=StudyStatus[study_val].value)
    await callback.message.delete()
    await callback.message.answer("O'quv holati yangilandi!", reply_markup=main_menu_kb())
    await state.clear()

@router.callback_query(ProfileSG.edit_age_range, F.data.startswith("age:"))
async def update_age_range(callback: CallbackQuery, state: FSMContext, user_repo: AbstractUserRepository):
    age_val = callback.data.split(":", 1)[1]
    await user_repo.update_profile(callback.from_user.id, age_range=AgeRange[age_val].value)
    await callback.message.delete()
    await callback.message.answer("Yosh toifasi yangilandi!", reply_markup=main_menu_kb())
    await state.clear()

@router.callback_query(F.data == "back_to_fields")
async def back_to_fields(callback: CallbackQuery, state: FSMContext):
    # Ensure user is in one of the relevant states (optional, but safer)
    current_state = await state.get_state()
    if current_state and current_state.startswith("ProfileSG:"):
        await callback.message.edit_text(
            "Qaysi ma'lumotni o'zgartirmoqchisiz?",
            reply_markup=edit_fields_kb()
        )
        await state.set_state(ProfileSG.main)

@router.message(ProfileSG.edit_name, F.text == "⬅️ Bekor qilish")
@router.message(ProfileSG.edit_phone, F.text == "⬅️ Bekor qilish")
@router.message(ProfileSG.edit_phone_2, F.text == "⬅️ Bekor qilish")
async def cancel_edit(message: Message, state: FSMContext, db_user, referral_repo: AbstractReferralRepository):
    await state.set_state(ProfileSG.main)
    count = await referral_repo.get_referral_count(db_user.telegram_id)
    text = (
        "👤 <b>Sizning profilingiz:</b>\n\n"
        f"🆔 ID: <b>{db_user.id}</b>\n"
        f"👤 Ism-familiya: <b>{db_user.full_name or db_user.first_name}</b>\n"
        f"📞 Telefon: <b>{db_user.phone_number or 'Kiritilmagan'}</b>\n"
        f"📞 Telefon 2: <b>{db_user.phone_number_2 or 'Kiritilmagan'}</b>\n"
        f"📍 Hudud: <b>{db_user.region or 'Kiritilmagan'}</b>\n"
        f"🎓 Holat: <b>{db_user.study_status or 'Kiritilmagan'}</b>\n"
        f"⏳ Yosh: <b>{db_user.age_range or 'Kiritilmagan'}</b>\n\n"
        f"💰 Balans: <b>{db_user.balance} ball</b>\n"
        f"👥 Takliflar: <b>{count} ta</b>\n"
    )
    await message.answer("Tahrirlash bekor qilindi.", reply_markup=main_menu_kb())
    await message.answer(text, parse_mode="HTML", reply_markup=profile_menu_kb())
