import os
import asyncio
import random
from datetime import datetime, time
from dateutil.relativedelta import relativedelta
import pytz
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder, CommandHandler, ContextTypes, CallbackQueryHandler
)

# 🔐 Токен
TOKEN = os.getenv("TOKEN")

# Московское время
timezone = pytz.timezone("Europe/Moscow")

# Дата отсчета
start_date = timezone.localize(datetime(2025, 9, 15, 21, 33))

# Эмодзи и цитаты
EMOJIS = ["🌹", "💖", "🐱", "🕊️", "💌", "✨", "💫", "🌸"]
QUOTES = [
    "С каждым днём я люблю тебя сильнее ❤️",
    "Ты — моё счастье каждый день 🌞",
    "Любовь наша растёт с каждой секундой 💖",
    "С тобой каждый момент волшебный ✨",
    "Ты делаешь мою жизнь ярче 🌟",
    "Моё сердце бьётся только для тебя 💓"
]
KISSES = ["😘", "😚", "💋", "😍"]

# Прогресс-бар
def progress_bar(total_days):
    length = 10
    filled = total_days % (length + 1)
    return "❤️" * filled + "⬜" * (length - filled)

# Формат времени
def format_time():
    now = datetime.now(timezone)
    if now < start_date:
        return "⏳ Эта дата ещё не наступила ❤️"
    diff = relativedelta(now, start_date)
    total_days = (now - start_date).days
    emoji = random.choice(EMOJIS)
    quote = random.choice(QUOTES)
    bar = progress_bar(total_days)
    return (
        f"{emoji} Наш счётчик любви {emoji}\n\n"
        f"🗓 {diff.years} лет\n"
        f"📅 {diff.months} месяцев\n"
        f"📆 {diff.days} дней\n"
        f"⏰ {diff.hours} часов\n"
        f"⏱ {diff.minutes} минут\n"
        f"⌛ {diff.seconds} секунд\n\n"
        f"{bar}\n\n"
        f"💌 {quote}"
    )

# Inline-кнопки
def get_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🔄 Обновить счётчик", callback_data="update")],
        [InlineKeyboardButton("🎁 Сюрприз", callback_data="surprise")],
        [InlineKeyboardButton("❤️ Отправить поцелуй", callback_data="kiss")]
    ])

# /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.message.chat_id
    if "chat_ids" not in context.application.bot_data:
        context.application.bot_data["chat_ids"] = set()
    context.application.bot_data["chat_ids"].add(chat_id)

    message = await update.message.reply_text(format_time(), reply_markup=get_keyboard())
    context.application.create_task(auto_update(message))
    await update.message.reply_text("Бот запущен и готов к любви! 💖")

# Автообновление
async def auto_update(message):
    while True:
        try:
            await asyncio.sleep(1)
            await message.edit_text(format_time(), reply_markup=get_keyboard())
        except:
            break

# Кнопки
async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if query.data == "update":
        await query.edit_message_text(format_time(), reply_markup=query.message.reply_markup)
    elif query.data == "surprise":
        surprise = random.choice(QUOTES + EMOJIS)
        await query.edit_message_text(f"🎉 Сюрприз: {surprise}", reply_markup=query.message.reply_markup)
    elif query.data == "kiss":
        await query.edit_message_text(f"{random.choice(KISSES)} Поцелуй отправлен!", reply_markup=query.message.reply_markup)

# Команды
async def love(update: Update, context: ContextTypes.DEFAULT_TYPE):
    quote = random.choice(QUOTES)
    await update.message.reply_text(f"💖 {quote}")

async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(format_time())

async def surprise_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    surprise = random.choice(QUOTES + EMOJIS)
    await update.message.reply_text(f"🎁 Сюрприз: {surprise}")

async def kiss_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f"{random.choice(KISSES)} Поцелуй отправлен!")

# Ежедневные уведомления
async def daily_notifications(app):
    while True:
        now = datetime.now(timezone)
        chat_ids = app.bot_data.get("chat_ids", set())

        # Доброе утро в 08:00
        if now.time() >= time(8, 0) and now.time() < time(8, 1):
            for chat_id in chat_ids:
                await app.bot.send_message(chat_id, f"🌞 Доброе утро! {format_time()}")

        # Спокойной ночи в 23:30
        if now.time() >= time(23, 30) and now.time() < time(23, 31):
            for chat_id in chat_ids:
                await app.bot.send_message(chat_id, f"🌙 Спокойной ночи! {format_time()}")

        await asyncio.sleep(60)

# Основное
app = ApplicationBuilder().token(TOKEN).build()

# Команды
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("love", love))
app.add_handler(CommandHandler("status", status))
app.add_handler(CommandHandler("surprise", surprise_cmd))
app.add_handler(CommandHandler("kiss", kiss_cmd))
app.add_handler(CallbackQueryHandler(button))

# Запуск уведомлений после старта
async def on_startup(app):
    app.create_task(daily_notifications(app))

app.post_init(on_startup)

print("Бот запущен ❤️")
app.run_polling()
