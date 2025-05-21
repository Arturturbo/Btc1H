import os
import pytz
import requests
from datetime import datetime, timedelta
from telegram import Bot, InlineKeyboardMarkup, InlineKeyboardButton

TOKEN = os.environ.get("TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")
bot = Bot(token=TOKEN)

def get_last_closed_candle_time():
    utc_now = datetime.utcnow().replace(minute=0, second=0, microsecond=0, tzinfo=pytz.utc)
    last_closed = utc_now - timedelta(hours=1)
    kyiv_time = last_closed.astimezone(pytz.timezone('Europe/Kyiv'))
    return last_closed, kyiv_time, last_closed.strftime('%Y%m%d_%H00')

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
    return f"""
📊 BTC 1H Анализ
🕒 Время: {utc_time.strftime('%Y-%m-%d %H:%M:%S')} UTC / {kyiv_time.strftime('%H:%M')} GMT+3
📈 Тип сигнала: {data['type']}
📏 RSI: {data['rsi']}
📊 MACD: {data['macd']}
📦 Объём: {data['volume']}
💥 OI Δ: {data['oi_delta']}
🧠 Рекомендация: {data['recommendation']}
🎯 Вероятность: {data['probability']}
""".strip()

def already_sent(report_id):
    return os.path.exists(f"{report_id}.sent")

def mark_sent(report_id):
    with open(f"{report_id}.sent", "w") as f:
        f.write("ok")

def send_to_telegram(text):
    keyboard = [
        [InlineKeyboardButton("✅ Вошёл", callback_data="entered"),
         InlineKeyboardButton("🚫 Пропустил", callback_data="skipped")]
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
if __name__ == "__main__":
