import asyncio
from aiogram import Bot, Dispatcher, F, types
from aiogram.enums import ParseMode
from aiogram.types import Message
from aiogram.client.default import DefaultBotProperties
from aiogram.filters import Command
import logging

# 🔐 TOKEN & ADMIN sozlamalari
BOT_TOKEN = "7796296335:AAFFUdOI_Qnj95VkGA8JaRzh-jJAclVOqug"  # ← Bot tokeningizni shu yerga yozing
ADMINS = [7752032178]  # ← Adminlar ID sini shu yerga yozing (ID foydalanuvchilarga ko‘rinmaydi)

# 📝 User bazasi (faqat ID saqlaymiz)
foydalanuvchilar = set()

# 📞 Adminlar uchun telefon raqamlari (foydalanuvchilarga ko‘rinadigan)
ADMIN_CONTACTS = """
📞 +998 94 089-81-19
"""  # Kerakli telefon raqamlaringizni shu yerga yozing

# 📋 /start komandasi
async def start_handler(message: Message):
    foydalanuvchilar.add(message.from_user.id)
    await message.answer(
        "👋 <b>Salom!</b>\n\n"
        "🛍 Kerakli mahsulot yoki xizmat nomini yozing.\n"
        "📨 Biz uni administratorlarga yetkazamiz va ular siz bilan tez orada bog‘lanadi.\n\n"
        "✏️ Marhamat, yozishni boshlang!",
        parse_mode=ParseMode.HTML
    )

# 📤 Foydalanuvchidan kelgan matn (so‘rov) adminlarga yuborish
async def text_handler(message: Message, bot: Bot):
    foydalanuvchilar.add(message.from_user.id)

    user_info = (
        f"💬 <b>Yangi so‘rov!</b>\n\n"
        f"👤 <b>Admin:</b> @{message.from_user.username or '🕵️ No username'}\n"
        f"{ADMIN_CONTACTS}\n"
        f"📩 <b>Xabar:</b> <i>{message.text}</i>"
    )

    for admin_id in ADMINS:
        try:
            await bot.send_message(admin_id, user_info, parse_mode=ParseMode.HTML)
        except Exception as e:
            logging.warning(f"Admin xatoligi: {e}")

    await message.answer(
        "🆗 <b>So‘rovingiz yuborildi!</b>\n"
        "📞 So‘rovingiz bo‘yicha adminlar bilan bog'laning.",
        parse_mode=ParseMode.HTML
    )

# 📣 /reklama komandasi – faqat adminlarga, hamma foydalanuvchilarga xabar yuboradi
async def reklama_handler(message: Message, bot: Bot):
    if message.from_user.id not in ADMINS:
        return await message.answer("🚫 Siz bu buyruqdan foydalana olmaysiz.")

    matn = message.text.replace("/reklama", "").strip()
    if not matn:
        return await message.answer("❗ Iltimos, reklama matnini yozing.\nMasalan:\n/reklama 🎉 Yangi aksiyalar boshlandi!")

    reklama_xabar = f"""
📢 <b>YANGI REKLAMA!</b>

{matn}

🔔 Bizni kuzatib boring!
"""

    count = 0
    for user_id in foydalanuvchilar:
        try:
            await bot.send_message(user_id, reklama_xabar, parse_mode=ParseMode.HTML)
            count += 1
        except:
            pass

    await message.answer(f"✅ Reklama {count} ta foydalanuvchiga yuborildi!")

# 👥 /foydalanuvchilar komandasi – adminlarga foydalanuvchilar sonini ko‘rsatadi
async def foydalanuvchilar_handler(message: Message):
    if message.from_user.id not in ADMINS:
        return await message.answer("🚫 Bu buyruq faqat administratorlar uchun.")

    await message.answer(
        f"👥 Botdan hozirgacha <b>{len(foydalanuvchilar)}</b> ta foydalanuvchi foydalangan.",
        parse_mode=ParseMode.HTML
    )

# 🔁 Botni ishga tushurish
async def main():
    bot = Bot(
        token=BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )
    dp = Dispatcher()

    dp.message.register(start_handler, Command("start"))
    dp.message.register(reklama_handler, F.text.startswith("/reklama"))
    dp.message.register(foydalanuvchilar_handler, Command("foydalanuvchilar"))
    dp.message.register(text_handler)  # Oddiy matn so‘rov uchun

    print("🤖 Bot ishga tushdi...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
