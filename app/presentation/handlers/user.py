
from aiogram import Router, F
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from urllib.parse import quote

from app.domain.repositories import AbstractUserRepository, AbstractReferralRepository
from app.use_cases.leaderboard import LeaderboardService
from app.config.settings import settings

router = Router()

@router.message(F.text == "➕ Ball yig‘ish")
async def show_points_and_link(
    message: Message,
    db_user,
    user_repo: AbstractUserRepository,
    referral_repo: AbstractReferralRepository,
    bot
):
    
    if not db_user:
        await message.answer("Siz ro'yxatdan o'tmagansiz, avval /start buyrug'i bilan ro'yxatdan o'ting.")
        return

    bot_info = await bot.get_me()
    link = f"https://t.me/{bot_info.username}?start={db_user.telegram_id}"
    
    # Text to share with friends
    share_text = (
        f"Assalomu alaykum, aziz hamkasbim! 🤝\n\n"
        f"Men hozirgina \"ROBOTRONIX\" jamoasining \"ZAMONAVIY USTOZ — 2025\" yirik loyihasida ishtirok etishni boshladim va buni sizga ham ilindim.\n\n"
        f"🎁 Nega sizga ham tavsiya qilyapman?\nChunki botga kirib, start bergan zahotingiz sizga ham 100 000 so‘mlik \"Ehtirom vaucheri\" taqdim etiladi! Bu vaucherdan 3 oy davomida istalgan o‘quv kurslari uchun foydalanish mumkin.\n\n"
        f"🏆 Tanlov sovg‘alari juda jiddiy (jami 39 ta):\nLoyiha doirasida quyidagi qimmatbaho sovrinlar o‘ynalmoqda:\n\n"
        f"🔹 9 ta professional Arduino to‘plamlari (RMT-1, 2, 3);\n"
        f"🔹 Yangi 5-sinf darsligi uchun maxsus o‘quv to‘plamlari\n"
        f"🔹 25 ta tayyor 3D Svetofor modellari;\n"
        f"💰 Jami 8 000 000 so‘mlik vaucherlar jamg‘armasi!\n"
        f"✨ Biz kabi texnologiya o‘qituvchilari uchun bu ham bilim, ham dars jarayonida kerak bo‘ladigan zamonaviy jihozlarni yutib olish uchun ajoyib imkoniyat!\n\n"
        f"Siz ham hoziroq ro‘yxatdan o‘ting va 100 000 so‘m bonusingizni oling: 👇 \n{link}"
    )
    share_url = f"https://t.me/share/url?&text={quote(share_text)}"
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="♻️ Do'stlarga ulashish", url=share_url)]
    ])
    
    text = (
        "Ustoz, sizda <b>39 ta qimmatbaho sovg'adan</b> birini yutib olish imkoniyati bor! 🏆\n\n"
        "💡 <b>Qanday ishtirok etasiz?</b>\n"
        "Pastdagi shaxsiy havolangizni hamkasblaringizga, maktab guruhlariga ulashing. "
        "Sizning havolangiz orqali ro'yxatdan o'tgan har bir hamkasbingiz uchun <b>10 ball</b> olasiz.\n\n"
        "✨ <b>Hozirning o'zida:</b> Sizga kurslarimiz uchun <b>100 000 so'mlik vaucher</b> taqdim etildi! "
        "Uni vebinar kuni ishlatishingiz mumkin.\n\n"
        f"🔗 <b>Sizning taklifnomangiz:</b>\n{link}"
    )
    await message.answer(text, parse_mode="HTML", reply_markup=keyboard)

@router.message(F.text == "💰 Ballarim")
async def show_my_points(
    message: Message,
    db_user,
    referral_repo: AbstractReferralRepository
):
    # Get stats
    if not db_user:
        await message.answer("Siz ro'yxatdan o'tmagansiz, avval /start buyrug'i bilan ro'yxatdan o'ting.")
        return

    count = await referral_repo.get_referral_count(db_user.telegram_id)
    points = db_user.balance
    
    text = (
        f"👤 <b>{db_user.full_name or db_user.first_name}</b>\n\n"
        f"🆔 ID: <b>{db_user.id}</b>\n"
        f"💰 Balans: <b>{points} ball</b>\n"
        f"👥 Takliflar: <b>{count} ta</b>"
    )
    await message.answer(text, parse_mode="HTML")


@router.message(F.text == "📊 Reyting (TOP-50)")
async def show_leaderboard(
    message: Message,
    user_repo: AbstractUserRepository,
    db_user
):
   
    if not db_user:
        await message.answer("Siz ro'yxatdan o'tmagansiz, avval /start buyrug'i bilan ro'yxatdan o'ting.")
        return

    service = LeaderboardService(user_repo)
    top_users = await service.get_top_users(limit=50)
    user_rank = await service.get_user_rank(db_user.telegram_id)
    
    text = "🏆 <b>Hozirgi yetakchilar:</b>\n\n"
    
    for idx, user in enumerate(top_users, 1):
        name = user.full_name if user.full_name else user.first_name
        text += f"{idx}. {name} — {user.balance} ball\n"
        
    text += f"\n\nSizning o'rningiz: <b>{user_rank}-o'rin</b>"
    
    await message.answer(text, parse_mode="HTML")

@router.message(F.text == "🎁 Sovg‘alar va Shartlar")
async def show_rewards(message: Message):
    text = (
        "<b>ZAMONAVIY USTOZ — 2025 tanlovi sovrinlari:</b>\n"
        "Tanlovda jami 39 ta qimmatbaho sovg‘a va 8 000 000 so‘mlik vaucherlar fondi mavjud! 🤩\n"
        "🏆 Referal reyting g‘oliblari uchun (botga odam qo‘shish orqali):\n"
        "🥇 1–2-o‘rinlar: RMT-3 To‘liq Arduino to‘plami.\n"
        "🥈 3–4-o‘rinlar: RMT-2 To‘liq Arduino to‘plami.\n"
        "🥉 5–9-o‘rinlar: RMT-1 To‘liq Arduino to‘plami.\n"
        "📗 10–14-o‘rinlar: 5-sinf darsligi uchun maxsus to‘plam.\n"
        "🚦 15–39-o‘rinlar: Svetofor 3D modeli (tayyor qurilma).\n\n"
        "🎟 Vebinar davomida o‘ynaladigan vaucherlar (Random orqali):\n"
        "💎 3 ta — 600,000 so‘mlik\n"
        "💎 3 ta — 400,000 so‘mlik\n"
        "💎 10 ta — 300,000 so‘mlik\n"
        "💎 10 ta — 200,000 so‘mlik\n\n\n"
        "<b>📜 TANLOV SHARTLARI:</b>\n"
        "1. Ball yig‘ish: Har bir taklif qilgan va ro‘yxatdan o‘tgan hamkasbingiz uchun 10 ball beriladi.\n"
        "2. Vaucherlar: Bir xaridda faqat bitta vaucherni ishlatish mumkin. Katta vaucherlar (300k+) faqat to‘liq to‘lov uchun amal qiladi.\n"
        " 3. Logistika: Sovg‘alarni yetkazib berish (pochta) xarajatlari g‘oliblar tomonidan qoplanadi.\n"
        " 4. Shaffoflik: G‘oliblar vebinar kuni jonli efirda aniqlanadi. Botda nakrutka ishlatganlar tanlovdan chetlatiladi.\n\n"
        " 🚀 Hozirdan ball yig‘ishni boshlang va o‘z sovg‘angizni band qiling!"
    )
    await message.answer(text, parse_mode="HTML")

@router.message(F.text == "🎓 Kurslar haqida")
async def show_courses(message: Message):
    text = (
        "<b>🎓 ROBOTRONIX BILAN KASBIY MAHORATINGIZNI OSHIRING!</b>\n"
        " Bizning kurslarimiz Texnologiya fani ustozlari uchun 4-chorak darslarini qo‘rquvsiz va yuqori saviyada o‘tishga mo‘ljallangan.\n"
        "<b>📦 TANLOV UCHUN 3 TA TA’LIM TARIFI:</b>\n\n"
        "🔸 <b>1️⃣ MUSTAQIL (500,000 so‘m)</b>\n"
        "Faqat video darslar va nazorat.\n"
        "Rasmiy muhrli (qog‘oz) sertifikat.\n"
        "Jihozlar berilmaydi.\n\n"
        "🔸 <b>2️⃣ PROFESSIONAL (1,400,000 so‘m) — 🔥 Eng ko‘p tanlanadigan paket!</b>\n"
        "RMT To‘plami (Arduino set) uyingizga yetkaziladi!\n"
        "Video darslar + Telegramda jonli video-aloqalar.\n"
        "QR kodli rasmiy sertifikat.\n"
        "Bonus: 5-sinf yangi darsligi moduli + Tayyor o‘quv rejasi.\n\n"
        "🔸 <b>3️⃣ EKSPERT (6,400,000 so‘m)</b>\n"
        "6 oylik chuqurlashtirilgan kurs (Robototexnika + SI).\n"
        "3 xil katta to‘plam: WeDo 2.0, Znatok 360, Arduino Mega.\n"
        "Ish bilan ta’minlash va filial ochish kafolati.\n\n\n"
        "<b>🎁 KURSNI BITIRGANDAGI IMKOZNIYATLAR:</b>\n"
        " 🎓 Grant: Har bir bitiruvchimizga o‘quvchisini o‘qitish uchun 400,000 so‘mlik vaucher beriladi.\n"
        "💰 Biznes imkoniyat: Kursni 75+ ball bilan bitirgan ustozlarning maktabida Robotronix filialini ochamiz, jihozlab beramiz va ustozni ishga olamiz!\n\n"
        "💳 To‘lov: 100k va 200k vaucher egalari uchun foizsiz bo‘lib to‘lash (nasiya) imkoniyati mavjud!\n"
        " 4-chorakni tanaffussiz, tayyor jihoz va bilim bilan boshlang! ✨\n\n"

    )
    await message.answer(text, parse_mode="HTML")

@router.message(F.text == "📞 Bog‘lanish")
async def show_contact(message: Message):
    text = (
        "<b>Biz bilan bog'lanish:</b>\n\n"
        "📞 Admin: @Robotronix_qabul\n"
        "☎️ Telefon: +998 33 803 33 53\n\n"

        "<b>Dasturchi bilan bog'lanish:</b>\n\n"
        "📞 Dasturchi: @Bilmadm_0\n"
    )
    await message.answer(text, parse_mode="HTML")
