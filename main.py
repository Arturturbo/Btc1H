
import requests
import time
from datetime import datetime
import logging
from telegram import Bot, InlineKeyboardButton, InlineKeyboardMarkup

# === НАСТРОЙКИ ===
TOKEN = "ВАШ_ТОКЕН"  # Заменить на твой Telegram токен
CHAT_ID = "ВАШ_CHAT_ID"  # Заменить на твой Chat ID

SYMBOL = "BTCUSDT"
INTERVAL = "1h"
API_URL = f"https://api.binance.com/api/v3/klines?symbol={SYMBOL}&interval={INTERVAL}&limit=100"

bot = Bot(token=TOKEN)

# === ПОЛУЧЕНИЕ RSI ===
def calculate_rsi(closes, period=14):
    gains, losses = [], []
    for i in range(1, len(closes)):
        change = closes[i] - closes[i - 1]
        gains.append(max(change, 0))
        losses.append(abs(min(change, 0)))
    avg_gain = sum(gains[-period:]) / period
    avg_loss = sum(losses[-period:]) / period
    rs = avg_gain / avg_loss if avg_loss != 0 else 0
    return 100 - (100 / (1 + rs))

# === ПОЛУЧЕНИЕ MACD ===
def calculate_macd(closes):
    def ema(data, period):
        k = 2 / (period + 1)
        ema_data = [sum(data[:period]) / period]
        for price in data[period:]:
            ema_data.append((price - ema_data[-1]) * k + ema_data[-1])
        return ema_data
    ema12 = ema(closes, 12)
    ema26 = ema(closes, 26)
    macd_line = [a - b for a, b in zip(ema12[-len(ema26):], ema26)]
    signal_line = ema(macd_line, 9)
    return macd_line[-1], signal_line[-1]

# === ОСНОВНОЙ АНАЛИЗ ===
def analyze_and_report():
    try:
        res = requests.get(API_URL)
        data = res.json()
        closes = [float(c[4]) for c in data]

        rsi = calculate_rsi(closes)
        macd, signal = calculate_macd(closes)
        macd_trend = "🔼 вверх" if macd > signal else "🔽 вниз"

        message = (
            f"📊 BTC 1H Анализ"

            f"🕒 Время: {datetime.utcnow().strftime('%Y-%m-%d %H:%M')} UTC"

            f"📈 RSI: {rsi:.2f}"

            f"📉 MACD: {macd:.4f} ({macd_trend})"

            f"📌 Рекомендация: {'Покупка' if rsi < 35 and macd > signal else 'Ожидание'}"
        )

        keyboard = [
            [InlineKeyboardButton("✅ Вошёл", callback_data="entered"),
             InlineKeyboardButton("🚫 Пропустил", callback_data="skipped")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        bot.send_message(chat_id=CHAT_ID, text=message, reply_markup=reply_markup)

    except Exception as e:
        logging.error(f"Ошибка анализа: {e}")
        bot.send_message(chat_id=CHAT_ID, text="⚠️ Ошибка анализа BTC 1H.")

# === ЗАПУСК КАЖДЫЙ ЧАС ===
if __name__ == "__main__":
    while True:
        analyze_and_report()
        time.sleep(3600)
