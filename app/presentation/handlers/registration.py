
from aiogram import Router, F
import logging
from aiogram.types import Message, CallbackQuery, FSInputFile, ReplyKeyboardRemove
from aiogram.filters import CommandStart, CommandObject
from aiogram.fsm.context import FSMContext
from sqlalchemy import select

from app.domain.repositories import AbstractUserRepository, AbstractReferralRepository
from app.use_cases.registration import RegistrationService
from app.use_cases.subscription import SubscriptionService
from app.presentation.states import RegistrationSG
from app.presentation.keyboards.registration import check_subscription_kb, phone_kb, regions_kb, study_status_kb, age_range_kb
from app.presentation.keyboards.main import main_menu_kb
from app.domain.enums import UserStatus, StudyStatus, AgeRange
from app.infrastructure.repositories.sqlalchemy import SQLAlchemyChannelRepository
from app.infrastructure.telegram.checker import TelegramChannelChecker
from app.infrastructure.database.models import User, WebinarCheckin

router = Router()

def get_reg_service(user_repo, referral_repo):
    return RegistrationService(user_repo, referral_repo)

@router.message(CommandStart())
async def cmd_start(
    message: Message, 
    command: CommandObject, 
    db_user, 
    user_repo: AbstractUserRepository, 
    referral_repo: AbstractReferralRepository,
    session,
    state: FSMContext,
    bot
):
    # Initialize services
    reg_service = get_reg_service(user_repo, referral_repo)
    
    referrer = None
    if command.args and command.args.isdigit():
        referrer = int(command.args)

    # Checkin Deep Link
    if command.args == "checkin":
        try:
            # 1. Register or update user info (always ensure fresh info)
            user = await reg_service.register_user(message.from_user.id, message.from_user.first_name, message.from_user.username, None)
            
            # 2. Check if user is ACTIVE (Full registration)
            if user.status == UserStatus.ACTIVE and user.phone_number:
                # Check duplicate
                stmt = select(WebinarCheckin).where(WebinarCheckin.user_id == message.from_user.id)
                result = await session.execute(stmt)
                existing_checkin = result.scalars().first()
                
                if existing_checkin:
                    await message.answer("ℹ️ <b>Siz allaqachon ro'yxatdasiz!</b>\n\nTakroriy ro'yxatdan o'tish shart emas.", parse_mode="HTML")
                    return

                # Log attendance
                checkin = WebinarCheckin(user_id=message.from_user.id)
                session.add(checkin)
                await session.commit()
                
                await message.answer("✅ <b>Rahmat!</b>\n\nSiz vebinar qatnashchisi sifatida muvaffaqiyatli ro'yxatga olindingiz! 🎉", parse_mode="HTML")
                return
            else:
                # User is NEW or Incomplete -> Redirect to Registration Flow (fall through)
                await state.update_data(is_checkin=True)
                await message.answer("👋 <b>Assalomu alaykum!</b>\n\nVebinarda qatnashish uchun avval ro'yxatdan o'tishingiz kerak.", parse_mode="HTML")
                # We do NOT return here, so it continues to the registration logic below
        except Exception as e:
            await session.rollback()
            logging.error(f"Checkin error: {e}", exc_info=True)
            await message.answer(f"❌ Xatolik yuz berdi: {e}")
            return

    # Register or get user

    # Register or get user
    # Note: If user exists, register_user just returns it. 
    # If using deep link, we might want to track referrer even if user exists but usually logic restricts to new users.
    user = await reg_service.register_user(message.from_user.id, message.from_user.first_name, message.from_user.username, referrer)
    
    if user.status == UserStatus.ACTIVE:
        await message.answer("Siz allaqachon ro‘yxatdan o‘tgansiz.", reply_markup=main_menu_kb())
        return

    # Start Flow
    # Check Channels
    channel_repo = SQLAlchemyChannelRepository(session)
    checker = TelegramChannelChecker(bot)
    sub_service = SubscriptionService(channel_repo, checker)
    
    is_subbed, unsubscribed = await sub_service.check_user_subscription(message.from_user.id)
    
    if is_subbed:
        # User is already subscribed to all channels, skip to Name
        await state.set_state(RegistrationSG.wait_name)
        await message.answer(text=("<b>Assalomu Alaykum!</b>\n\nIsm-sharifingizni yuboring. \nBu ism kelgusida sertifikatlaringizda ham aks etadi. ✨"), parse_mode="HTML")
        return

    await state.set_state(RegistrationSG.wait_channel)
    text = (
        "Assalomu alaykum, aziz va fidoyi ustoz! 👋\n\n"
        "Sizni <b>\"ZAMONAVIY USTOZ — 2025\"</b> respublika tanlovida ko‘rib turganimizdan juda mamnunmiz. "
        "Ushbu loyiha orqali siz robototexnika dunyosiga oson kirib borasiz va zamonaviy ta'lim texnologiyalarini o'zlashtirasiz.\n\n"
        "🎁 Tanlovda ishtirok etish va 100 000 so'mlik vaucherga ega bo'lish uchun quyidagi kanallarimizga a'zo bo'ling. "
        "Bu sizga yangiliklardan birinchi bo'lib xabardor bo'lish imkonini beradi:"
    )
    for ch in unsubscribed:
        text += f"👉 <a href='{ch.link}'>{ch.name}</a>\n"
        
    await message.answer(text, parse_mode="HTML", reply_markup=check_subscription_kb(unsubscribed))


@router.callback_query(F.data == "check_subscription")
async def on_check_subscription(
    callback: CallbackQuery,
    user_repo: AbstractUserRepository,
    referral_repo: AbstractReferralRepository,
    session,
    state: FSMContext,
    bot,
    db_user
):
    channel_repo = SQLAlchemyChannelRepository(session)
    checker = TelegramChannelChecker(bot)
    sub_service = SubscriptionService(channel_repo, checker)
    
    # SAFEGUARD: If db_user is None (e.g. after restore), use telegram ID directly
    telegram_id = db_user.telegram_id if db_user else callback.from_user.id
    
    is_subbed, unsubscribed = await sub_service.check_user_subscription(telegram_id)
    
    if is_subbed:
        # If user is in registration flow
        if db_user and db_user.status == UserStatus.NEW:
            # Move to Name step
            await state.set_state(RegistrationSG.wait_name)
            await callback.message.delete()
            await callback.message.answer(text=("<b>Rahmat!\nEndi Roʻyxatdan oʻtishni boshlaymiz!</b> ✅\n\nIsm-sharifingizni yuboring. \nBu ism kelgusida sertifikatlaringizda ham aks etadi. ✨"), parse_mode="HTML")
        elif db_user:
            # Active user triggered by middleware
            await callback.message.delete()
            await callback.message.answer("Siz yana botdan foydalanishingiz mumkin! ✅", reply_markup=main_menu_kb())
            await callback.answer()
        else:
            # Case where user is NOT in DB (db_user is None) but passed subs check
            # We must register them or ask to start
            await callback.message.delete()
            await callback.message.answer("Iltimos, qaytadan ro'yxatdan o'tish uchun /start ni bosing.")
            await callback.answer()
    else:
        text = "Siz quyidagi kanallarga hali obuna bo‘lmadingiz:\n\n"
        for ch in unsubscribed:
            text += f"👉 <a href='{ch.link}'>{ch.name}</a>\n"
        await callback.answer("Hali to‘liq obuna bo‘lmadingiz! ❌", show_alert=True)
        # Re-send or edit with new keyboard if needed, but the old message already has buttons.
        # Actually, let's update the message to be sure they have the latest links.
        try:
            await callback.message.edit_text(text, parse_mode="HTML", reply_markup=check_subscription_kb(unsubscribed))
        except Exception:
            # Message is maybe the same, ignore
            pass


@router.message(RegistrationSG.wait_name, F.text)
async def process_name(message: Message, state: FSMContext):
    await state.update_data(full_name=message.text)
    await state.set_state(RegistrationSG.wait_phone)
    text = (
        "Rahmat! Endi siz bilan bog'lanishimiz uchun "
        "telefon raqamingizni pastdagi tugma orqali yuboring. 📱\n\n"
        "<i>Eslatma: Faqat \"Kontaktni yuborish\" tugmasini bosishingiz kifoya.</i>"
    )
    await message.answer(text, parse_mode="HTML", reply_markup=phone_kb())


@router.message(RegistrationSG.wait_phone, F.contact)
async def process_phone(message: Message, state: FSMContext, user_repo: AbstractUserRepository):
    phone = message.contact.phone_number
    
    # Check if phone is already registered
    existing_user = await user_repo.get_user_by_phone(phone)
    if existing_user and existing_user.telegram_id != message.from_user.id:
        await message.answer(
            "⚠️ Ushbu telefon raqami allaqachon ro'yxatdan o'tgan! "
            "Iltimos, o'zingizga tegishli raqamni yuboring yoki admin bilan bog'laning."
        )
        return

    await state.update_data(phone_number=phone)
    
    # Move to Region
    await state.set_state(RegistrationSG.wait_region)
    text = (
        "Ajoyib! Qaysi viloyatda faoliyat yuritishingizni tanlang. "
        "Bu bizga sizning hududingizdagi maktablar bilan hamkorlik qilishda asqotadi. 📍"
    )
    await message.answer(text, reply_markup=regions_kb())


# Fallback for phone if user sends text instad of contact (optional validation)
@router.message(RegistrationSG.wait_phone)
async def process_phone_invalid(message: Message):
    await message.answer("Iltimos, pastdagi tugmani bosib telefon raqamingizni yuboring.", reply_markup=phone_kb())

@router.callback_query(RegistrationSG.wait_region, F.data.startswith("region:"))
async def process_region(
    callback: CallbackQuery,
    user_repo: AbstractUserRepository,
    referral_repo: AbstractReferralRepository,
    state: FSMContext,
    db_user
):
    region_val = callback.data.split(":", 1)[1]
    await state.update_data(region=region_val)
    
    # Move to Study Status
    await state.set_state(RegistrationSG.wait_study_status)
    await callback.message.edit_text("Robotronix markazida avval tahsil olganmisiz?", reply_markup=study_status_kb())

@router.callback_query(RegistrationSG.wait_study_status, F.data.startswith("study:"))
async def process_study_status(callback: CallbackQuery, state: FSMContext):
    study_val = callback.data.split(":", 1)[1]
    await state.update_data(study_status=StudyStatus[study_val].value)
    
    await state.set_state(RegistrationSG.wait_age_range)
    await callback.message.edit_text("Yoshingizni tanlang:", reply_markup=age_range_kb())

@router.callback_query(RegistrationSG.wait_age_range, F.data.startswith("age:"))
async def process_age_range(
    callback: CallbackQuery,
    user_repo: AbstractUserRepository,
    referral_repo: AbstractReferralRepository,
    state: FSMContext,
    db_user
):
    age_val = callback.data.split(":", 1)[1]
    await state.update_data(age_range=AgeRange[age_val].value)
    
    data = await state.get_data()
    full_name = data.get("full_name")
    phone_number = data.get("phone_number")
    region = data.get("region")
    study_status = data.get("study_status")
    age_range = data.get("age_range")
    
    reg_service = get_reg_service(user_repo, referral_repo)
    
    # Update Profile and Complete Registration
    try:
        # Update Profile
        await reg_service.update_user_profile(
            db_user.telegram_id, 
            full_name=full_name, 
            phone_number=phone_number, 
            region=region,
            study_status=study_status,
            age_range=age_range
        )
        
        # Complete Registration (Activates user, gives bonus)
        referrer_id, points_awarded = await reg_service.complete_registration(db_user.telegram_id)
        
        # Notify Referrer (only if points were awarded)
        if referrer_id and points_awarded:
            try:
                await callback.bot.send_message(
                    chat_id=referrer_id,
                    text=(
                        f"👤 <b>Yangi Foydalanuvchi!</b>\n\n"
                        f"Tabriklaymiz! <b>{db_user.full_name or db_user.first_name}</b> sizning havolangiz orqali ro'yxatdan o'tdi.\n"
                        f"Sizga <b>10 ball</b> taqdim etildi! ✨"
                    ),
                    parse_mode="HTML"
                )
            except Exception:
                # Referrer might have blocked the bot, ignore
                pass
                
    except Exception as e:
        logging.error(f"Registration Error for user {db_user.telegram_id}: {e}", exc_info=True)
        await callback.message.answer("❌ Ro'yxatdan o'tishda xatolik yuz berdi. Iltimos qaytadan urinib ko'ring yoki adminga murojaat qiling.")
        await state.clear()
        return
    
    try:
        await callback.message.delete()
    except Exception:
        pass
    
    # Check if this registration was triggered by Check-in
    is_checkin = data.get("is_checkin")
    if is_checkin:
        from app.infrastructure.database.models import WebinarCheckin
        try:
            # Check duplicate first (though unlikely for new user)
            stmt = select(WebinarCheckin).where(WebinarCheckin.user_id == db_user.telegram_id)
            result = await user_repo.session.execute(stmt)
            existing = result.scalars().first()
            
            if not existing:
                checkin = WebinarCheckin(user_id=db_user.telegram_id)
                user_repo.session.add(checkin)
                await user_repo.session.commit()
                
            await callback.message.answer("✅ <b>Siz muvaffaqiyatli qo'shildingiz!</b>", parse_mode="HTML", reply_markup=main_menu_kb())
        except Exception as e:
            logging.error(f"Failed to auto-checkin new user: {e}")
            await callback.message.answer("✅ <b>Siz muvaffaqiyatli ro'yxatdan o'tdingiz!</b>", parse_mode="HTML", reply_markup=main_menu_kb())
            
        await state.clear()
        return

    # Send Success Message (Standard Registration)
    text = (
        f"🎉 <b>Tabriklaymiz, {full_name}!</b>\n\n"
        "Siz \"ZAMONAVIY USTOZ — 2025\" loyihasida ishtirok etish uchun muvaffaqiyatli ro‘yxatdan o‘tdingiz!\n\n"
        "Siz endi zamonaviy va intiluvchan pedagoglar safidasiz. Sizga kasbiy o‘sishingiz yo‘lidagi kichik investitsiyamiz — 100 000 so‘mlik \"Ehtirom vaucheri\" taqdim etildi! 💳 \n\n"
        "💡 Vaucherdan qanday foydalanish mumkin? \nUni 3 oy davomida istalgan kurslarimiz uchun to‘lov sifatida ishlatishingiz mumkin.\n\n"
        "🌟 Ko‘proq yutishni xohlaysizmi?\nDo‘stlaringizni taklif qiling va sovg‘alar kolleksiyasini yig‘ing:\n\n"
        "✨ Hamkasbingizga tuhfa: Siz orqali ro‘yxatdan o‘tgan har bir ustozga ham 100 000 so‘m vaucher beriladi.\n📈 Sizga esa ball: Har bir taklifingiz uchun +10 ball yig‘asiz.\n\n"
        "🎁 Ballar evaziga qanday sovg‘alar kutmoqda?\n39 ta asosiy sovrin: 9 ta Arduino to'plam (RMT-1,2,3), 5-sinf to‘plamlari va 25 ta tayyor 3D Svetofor modellari! umumiy qiymati 8 000 000 so‘mlik vaucherlar!\n\n"
        "🔗 Pastdagi \"+Ball yig‘ish\" tugmasini bosing, maxsus e’lonni hamkasblaringizga ulashing va g‘oliblik sari qadam tashlang!\n\n"
        "Fursatni boy bermang, sovg‘alar sizni kutmoqda! 😊\n\n"
    )

    await callback.message.answer(text, parse_mode="HTML", reply_markup=main_menu_kb())
    await state.clear()


