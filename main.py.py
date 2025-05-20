
import requests
import time
from datetime import datetime

# Конфигурация
TOKEN = "YOUR_TELEGRAM_BOT_TOKEN"
CHAT_ID = "YOUR_TELEGRAM_CHAT_ID"

# Пример логики сигнала (симулировано)
def analyze_market():
    signal = {
        "time": datetime.utcnow().strftime("%Y-%m-%d %H:%M"),
        "type": "Bullish Engulfing",
        "rsi": 42.3,
        "macd_cross": True,
        "volume": "High",
        "oi_delta": "+5.3%",
        "recommendation": "Entry possible with confirmation",
        "probability": "74%"
    }
    return signal

# Отправка сигнала в Telegram
def send_to_telegram(signal):
    message = f"""
🕒 1H BTC Signal — {signal['time']}
🔹 Type: {signal['type']}
📈 RSI: {signal['rsi']}
📊 Volume: {signal['volume']}
📉 OI Δ: {signal['oi_delta']}
💬 Recommendation: {signal['recommendation']}
🎯 Probability: {signal['probability']}
"""
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    data = {"chat_id": CHAT_ID, "text": message, "parse_mode": "HTML"}
    requests.post(url, data=data)

# Имитация работы
if __name__ == "__main__":
    signal = analyze_market()
    send_to_telegram(signal)
