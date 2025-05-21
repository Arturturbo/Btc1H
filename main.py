import requests
import time
from datetime import datetime
from telegram import Bot, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.constants import ParseMode
from telegram.ext import ApplicationBuilder, CallbackQueryHandler, ContextTypes, CommandHandler

import os

TOKEN = os.environ.get("TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")

# История сигналов для предотвращения спама
last_signal_time = 0

async def start(update, context):
    await update.message.reply_text("Бот запущен и работает!")

async def button_handler(update, context):
    query = update.callback_query
    await query.answer()
    if query.data == "entered":
        await query.edit_message_reply_markup(reply_markup=None)
        await query.message.reply_text("✅ Вход зафиксирован.")
    elif query.data == "skipped":
        await query.edit_message_reply_markup(reply_markup=None)
        await query.message.reply_text("🚫 Пропуск зафиксирован.")

async def send_report(context: ContextTypes.DEFAULT_TYPE):
    global last_signal_time
    now = time.time()
    if now - last_signal_time < 3600:
        return  # Пропускаем, если ещё не прошло 1 час

    last_signal_time = now

    # Пример анализа (заглушка)
    signal_type = "Bullish engulfing"
    rsi = 36.7
    macd = "🔼 пересечение вверх"
    volume = "высокий"
    oi_delta = "+5.2%"
    recommendation = "✅ Возможен вход (при подтверждении)"
    probability = "78%"

    timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")

    message = (
        "📊 <b>BTC 1H Анализ</b>\n"
        f"🕒 <b>Время:</b> {timestamp} UTC\n"
        f"📈 <b>Тип сигнала:</b> {signal_type}\n"
        f"📉 <b>RSI:</b> {rsi}\n"
        f"📊 <b>MACD:</b> {macd}\n"
        f"📦 <b>Объём:</b> {volume}\n"
        f"💥 <b>OI Δ:</b> {oi_delta}\n"
        f"🧠 <b>Рекомендация:</b> {recommendation}\n"
        f"🎯 <b>Вероятность:</b> {probability}"
    )

    keyboard = [
        [
            InlineKeyboardButton("✅ Вошёл", callback_data="entered"),
            InlineKeyboardButton("🚫 Пропустил", callback_data="skipped")
        ]
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)
    await context.bot.send_message(
        chat_id=CHAT_ID,
        text=message,
        reply_markup=reply_markup,
        parse_mode=ParseMode.HTML
    )

if __name__ == "__main__":
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))

    # Запускаем задачу каждый час
    job_queue = app.job_queue
    job_queue.run_repeating(send_report, interval=3600, first=10)

    print("✅ Бот запущен")
    app.run_polling()
