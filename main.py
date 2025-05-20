import os
import time
import requests
from datetime import datetime
from telegram import Bot, InlineKeyboardMarkup, InlineKeyboardButton, Update
from telegram.ext import Updater, CallbackQueryHandler, CommandHandler, CallbackContext

# Переменные среды
TOKEN = os.getenv("TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
bot = Bot(token=TOKEN)

last_sent_time = None

def analyze_market():
    now = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
    signal = {
        "time": now,
        "type": "Bullish engulfing",
        "rsi": 36.7,
        "macd": "🔼 пересечение вверх",
        "volume": "высокий",
        "oi_delta": "+5.2%",
        "recommendation": "✅ Возможен вход (при подтверждении)",
        "probability": "78%"
    }
    return signal

def send_to_telegram(signal):
    global last_sent_time
    if signal["time"] == last_sent_time:
        print("[INFO] Сигнал уже был отправлен ранее.")
        return

    message = f"""📊 BTC 1H Анализ
🕒 Время: {signal['time']}
📈 Тип сигнала: {signal['type']}
📉 RSI: {signal['rsi']}
📊 MACD: {signal['macd']}
📦 Объём: {signal['volume']}
💥 OI Δ: {signal['oi_delta']}
🧠 Рекомендация: {signal['recommendation']}
🎯 Вероятность: {signal['probability']}"""

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("✅ Вошёл", callback_data="entered"),
         InlineKeyboardButton("🚫 Пропустил", callback_data="skipped")]
    ])

    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    data = {
        "chat_id": CHAT_ID,
        "text": message,
        "parse_mode": "HTML",
        "reply_markup": keyboard.to_json()
    }

    try:
        response = requests.post(url, data=data)
        if response.status_code == 200:
            print("[OK] Сообщение отправлено")
            last_sent_time = signal["time"]
        else:
            print(f"[ERROR] Код ответа Telegram: {response.status_code}, текст: {response.text}")
    except Exception as e:
        print(f"[ERROR] Ошибка при отправке сообщения: {e}")

def handle_response(update: Update, context: CallbackContext):
    response = update.callback_query.data
    user = update.effective_user.first_name
    update.callback_query.answer()
    update.callback_query.edit_message_reply_markup(reply_markup=None)
    update.callback_query.message.reply_text(
        f"{user} нажал: {'✅ Вошёл' if response == 'entered' else '🚫 Пропустил'}"
    )

if __name__ == "__main__":
    from telegram.ext import Updater
    updater = Updater(token=TOKEN, use_context=True)
    dp = updater.dispatcher
    dp.add_handler(CallbackQueryHandler(handle_response))
    updater.start_polling()

    while True:
        signal = analyze_market()
        send_to_telegram(signal)
        time.sleep(3600)
