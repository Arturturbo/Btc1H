import os
import requests
from datetime import datetime

def analyze_market():
    signal = {
        "time": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"),
        "type": "Long",
        "rsi": 58,
        "macd": "Positive crossover",
        "volume": "Rising",
        "oi_delta": "+3.4%",
        "recommendation": "Entry possible with confirmation",
        "probability": "74%"
    }
    print("[INFO] Сигнал сформирован:", signal)
    return signal

def send_to_telegram(signal):
    TOKEN = os.getenv("TOKEN")
    CHAT_ID = os.getenv("CHAT_ID")
    if not TOKEN or not CHAT_ID:
        print("[ERROR] Переменные окружения TOKEN или CHAT_ID не заданы.")
        return

    message = f"""
📊 BTC 1H Анализ

🔷 Type: {signal['type']}
📈 RSI: {signal['rsi']}
📊 MACD: {signal['macd']}
📉 Volume: {signal['volume']}
📍 OI Δ: {signal['oi_delta']}
📢 Recommendation: {signal['recommendation']}
🎯 Probability: {signal['probability']}
⏱ Time: {signal['time']}
"""
    print("[INFO] Попытка отправки в Telegram")

    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    data = {"chat_id": CHAT_ID, "text": message, "parse_mode": "HTML"}

    try:
        response = requests.post(url, data=data)
        if response.status_code == 200:
            print("[INFO] Успешно отправлено! ✅")
        else:
            print(f"[ERROR] Не удалось отправить сообщение. Код: {response.status_code}, ответ: {response.text}")
    except Exception as e:
        print(f"[ERROR] Ошибка при отправке сообщения: {e}")

if __name__ == "__main__":
    signal = analyze_market()
    send_to_telegram(signal)
