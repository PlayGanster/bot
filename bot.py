import logging
import re
import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes
from telegram.constants import ParseMode

from config import TELEGRAM_TOKEN, CHANNEL_ID, CHANNEL_URL, DIANA_TG, VK_REVIEWS
from database import init_db, create_or_update_user, get_user
from numerology import get_full_report

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

async def check_subscription(update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
    user_id = update.effective_user.id
    try:
        member = await context.bot.get_chat_member(chat_id=CHANNEL_ID, user_id=user_id)
        return member.status in ['member', 'administrator', 'creator']
    except Exception:
        return False

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    await create_or_update_user(user.id, user.username, user.full_name)
    
    if not await check_subscription(update, context):
        keyboard = [
            [InlineKeyboardButton("✨ Заглянуть в мой канал", url=CHANNEL_URL)],
            [InlineKeyboardButton("✅ Я с вами!", callback_data='check_sub')]
        ]
        await update.message.reply_text(
            f"Здравствуйте! ✨ Я — Диана.\n\n"
            "Рада приветствовать вас. Я помогаю людям находить ответы в их дате рождения и менять жизнь через осознанные практики.\n\n"
            "Чтобы я могла сделать для вас расчет, подпишитесь на мой канал. Там я каждый день делюсь прогнозами, практиками и важными инсайтами. Как подпишетесь — нажмите кнопку ниже, и мы начнем. 👇",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
    else:
        await show_main_menu(update, context)

async def show_main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        "Рада продолжению нашего общения! ✨\n\n"
        "Что для вас сейчас наиболее актуально? Выбирайте подходящий вариант:"
    )
    keyboard = [
        [InlineKeyboardButton("🔮 Узнать свою Матрицу", callback_data='get_reading')],
        [InlineKeyboardButton("🕯 Библиотека практик", callback_data='private_info')],
        [InlineKeyboardButton("💌 Написать мне лично", url=DIANA_TG)],
        [InlineKeyboardButton("💬 Почитать отзывы", url=VK_REVIEWS)]
    ]
    if update.message:
        await update.message.reply_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode=ParseMode.MARKDOWN)
    else:
        await update.callback_query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode=ParseMode.MARKDOWN)

async def show_private_info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        "Я создала особенное пространство — мой **приватный канал с практиками**. 🕯\n\n"
        "Это база знаний, которую я собирала долгое время. Там собраны проверенные инструменты: ритуалы на внутреннюю силу, проработки финансовых блоков и медитации для настройки на нужные состояния.\n\n"
        "Если вы чувствуете готовность к глубоким переменам и хотите получить доступ к эксклюзивным материалам — я буду рада видеть вас в нашем сообществе. Это важный шаг к новому качеству жизни."
    )
    keyboard = [
        [InlineKeyboardButton("✨ Узнать подробнее о доступе", url=DIANA_TG)],
        [InlineKeyboardButton("⬅️ Вернуться назад", callback_data='main_menu')]
    ]
    
    if update.message:
        await update.message.reply_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode=ParseMode.MARKDOWN)
    else:
        await update.callback_query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode=ParseMode.MARKDOWN)

async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    if query.data == 'check_sub':
        if await check_subscription(update, context):
            await show_main_menu(update, context)
        else:
            await query.message.reply_text("Кажется, подписка еще не подтверждена. Пожалуйста, подпишитесь на канал, чтобы мы могли продолжить. ✨")
    elif query.data == 'get_reading':
        await query.edit_message_text("Напишите вашу дату рождения (например, `15.05.1990`). Я проанализирую ваши цифры и подготовлю разбор... ✨", parse_mode=ParseMode.MARKDOWN)
    elif query.data == 'private_info':
        await show_private_info(update, context)
    elif query.data == 'main_menu':
        await show_main_menu(update, context)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await check_subscription(update, context):
        await start(update, context)
        return

    text = update.message.text
    if re.match(r'^\d{2}\.\d{2}\.\d{4}$', text):
        report = get_full_report(text)
        
        keyboard = [
            [InlineKeyboardButton("💎 Разобрать мою ситуацию лично", url=DIANA_TG)],
            [InlineKeyboardButton("🕯 Хочу в библиотеку практик", callback_data='private_info')]
        ]
        await update.message.reply_text(report, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode=ParseMode.MARKDOWN)
    else:
        await show_main_menu(update, context)

async def main():
    await init_db()
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(handle_callback))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    print("Бот Дианы запущен...")
    await app.run_polling()

if __name__ == '__main__':
    import asyncio
    asyncio.run(main())
