import os
import pytz
import requests
from datetime import datetime, timedelta
from telegram import Bot, InlineKeyboardMarkup, InlineKeyboardButton

TOKEN = os.environ.get("TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")
bot = Bot(token=TOKEN)

def get_last_closed_candle_time():
    utc_now = datetime.utcnow().replace(minute=0, second=0, microsecond=0)
    last_closed = utc_now - timedelta(hours=1)
    kyiv_time = last_closed.astimezone(pytz.timezone("Europe/Kyiv"))
    report_id = f"BTC_1H_{kyiv_time.strftime('%Y-%m-%d_%H')}"
    return last_closed, kyiv_time, report_id

def already_sent(report_id):
    return os.path.exists(f"{report_id}.sent")

def mark_sent(report_id):
    with open(f"{report_id}.sent", "w") as f:
        f.write("ok")

def fetch_mock_data():
    return {
        "type": "Bullish engulfing",
        "rsi": 36.7,
        "macd": "пересечение вверх",
        "volume": "высокий",
        "oi_delta": "+5.2%",
        "recommendation": "✅ Возможен вход (при подтверждении)",
        "probability": "78%"
    }

def format_report(data, utc_time, kyiv_time):
    return (
        f"📊 BTC 1H Анализ\n"
        f"🕓 Время: {kyiv_time.strftime('%Y-%m-%d %H:%M:%S')} (Киев)\n"
        f"📈 Тип сигнала: {data['type']}\n"
        f"📉 RSI: {data['rsi']}\n"
        f"📊 MACD: {data['macd']}\n"
        f"📦 Объём: {data['volume']}\n"
        f"💥 OI Δ: {data['oi_delta']}\n"
        f"🧠 Рекомендация: {data['recommendation']}\n"
        f"🎯 Вероятность: {data['probability']}"
    )

def send_to_telegram(text):
    keyboard = [
        [InlineKeyboardButton("✅ Вошёл", callback_data="entered"),
         InlineKeyboardButton("⛔ Пропустил", callback_data="skipped")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    bot.send_message(chat_id=CHAT_ID, text=text, reply_markup=reply_markup)

def main():
    utc_time, kyiv_time, report_id = get_last_closed_candle_time()
    if already_sent(report_id):
        return
    data = fetch_mock_data()
    message = format_report(data, utc_time, kyiv_time)
    send_to_telegram(message)
    mark_sent(report_id)

if__ name__ == "__main__":    main()
