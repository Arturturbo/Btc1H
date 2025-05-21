import os
import logging
import requests
from datetime import datetime, timedelta
from telegram import Bot, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CallbackQueryHandler, CommandHandler
import random

TOKEN = os.getenv("TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

def fetch_data():
    return {
        "time": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"),
        "pattern": "Bullish engulfing",
        "rsi": 36.7,
        "macd_signal": "пересечение вверх",
        "volume": "высокий",
        "oi_delta": "+5.2%",
        "recommendation": "✅ Возможен вход (при подтверждении)",
        "probability": "78%"
    }

def send_report(context):
    signal = fetch_data()
    message = (
        "📊 <b>BTC 1H Анализ</b>\n"
        f"🕒 <b>Время:</b> {signal['time']} UTC\n"
        f"📈 <b>Тип сигнала:</b> {signal['pattern']}\n"
        f"📉 <b>RSI:</b> {signal['rsi']}\n"
        f"📊 <b>MACD:</b> 🔼 {signal['macd_signal']}\n"
        f"📦 <b>Объём:</b> {signal['volume']}\n"
        f"💥 <b>OI Δ:</b> {signal['oi_delta']}\n"
        f"🧠 <b>Рекомендация:</b> {signal['recommendation']}\n"
        f"🎯 <b>Вероятность:</b> {signal['probability']}"
    )
    keyboard = [
        [InlineKeyboardButton("✅ Вошёл", callback_data="entered"),
         InlineKeyboardButton("🚫 Пропустил", callback_data="skipped")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    context.bot.send_message(chat_id=CHAT_ID, text=message, parse_mode="HTML", reply_markup=reply_markup)

def start(update, context):
    update.message.reply_text("Бот активен. Отчёты будут приходить каждый час.")

def handle_button(update, context):
    query = update.callback_query
    query.answer()
    response = "Отметка: вы " + ("вошли ✅" if query.data == "entered" else "пропустили 🚫")
    query.edit_message_reply_markup(reply_markup=None)
    context.bot.send_message(chat_id=query.message.chat_id, text=response)

def main():
    updater = Updater(token=TOKEN, use_context=True)
    dispatcher = updater.dispatcher
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CallbackQueryHandler(handle_button))
    job = updater.job_queue
    job.run_repeating(send_report, interval=3600, first=10)
    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main()