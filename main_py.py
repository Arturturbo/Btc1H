
import requests
from datetime import datetime
import os

# Получение переменных из среды
TOKEN = os.environ.get("TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")

def analyze_market():
    signal = {
        "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "type": "🔍 Analysis",
        "rsi": "Neutral",
        "macd": "Bearish",
        "volume": "High",
        "oi_delta": "+3.2%",
        "recommendation": "Entry possible with confirmation",
        "probability": "74%"
    }
    return signal

def send_to_telegram(signal):
    message = f"""📊 BTC 1H Анализ ({signal['time']})
🧭 Тип: {signal['type']}
📉 RSI: {signal['rsi']}
📈 MACD: {signal['macd']}
📊 Объём: {signal['volume']}
📦 OI Δ: {signal['oi_delta']}
🧠 Рекомендация: {signal['recommendation']}
🎯 Вероятность: {signal['probability']}"""

    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    data = {
        "chat_id": CHAT_ID,
        "text": message,
        "parse_mode": "HTML"
    }
    requests.post(url, data=data)

if __name__ == "__main__":
    signal = analyze_market()
    send_to_telegram(signal)
