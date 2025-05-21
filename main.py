import os
import logging
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Bot
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler
from datetime import datetime

TOKEN = os.environ.get("TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")

logging.basicConfig(level=logging.INFO)

def start(update, context):
    message = (
        f"📊 BTC 1H Анализ\n"
        f"⏰ Время: {datetime.utcnow().strftime('%Y-%m-%d %H:%M')} UTC\n"
        f"📉 Тип сигнала: Bullish engulfing\n"
        f"📈 RSI: 36.7\n"
        f"📊 MACD: 🔼 пересечение вверх\n"
        f"📦 Объём: высокий\n"
        f"💥 OI Δ: +5.2%\n"
        f"🧠 Рекомендация: ✅ Возможен вход (при подтверждении)\n"
        f"🎯 Вероятность: 78%"
    )

    keyboard = [
        [InlineKeyboardButton("✅ Вошёл", callback_data='entered'),
         InlineKeyboardButton("🚫 Пропустил", callback_data='skipped')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text(message, reply_markup=reply_markup)

def button(update, context):
    query = update.callback_query
    query.answer()
    query.edit_message_reply_markup(reply_markup=None)
    context.bot.send_message(chat_id=CHAT_ID, text=f"Пользователь выбрал: {query.data}")

def main():
    updater = Updater(token=TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CallbackQueryHandler(button))

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
