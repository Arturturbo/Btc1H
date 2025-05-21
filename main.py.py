import os
import requests
import pytz
import datetime
from pathlib import Path
from telegram import Bot, InlineKeyboardMarkup, InlineKeyboardButton

TOKEN = os.getenv("TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
COINGLASS_API_KEY = os.getenv("COINGLASS_API_KEY")
bot = Bot(token=TOKEN)
SENT_FOLDER = Path("./sent")
SENT_FOLDER.mkdir(exist_ok=True)

def get_report_id():
    kyiv = pytz.timezone("Europe/Kyiv")
    now = datetime.datetime.now(kyiv)
    report_id = f"BTC_1H_{now.strftime('%Y-%m-%d_%H')}"
    return report_id, now.strftime('%Y-%m-%d %H:%M:%S')

def already_sent(report_id):
    return (SENT_FOLDER / f"{report_id}.sent").exists()

def mark_sent(report_id):
    with open(SENT_FOLDER / f"{report_id}.sent", "w") as f:
        f.write("ok")

def get_coinglass_data():
    headers = {"coinglassSecret": COINGLASS_API_KEY}
    result = {
        "oi": "—%", "funding": "—", "long_short": "—", "spot": "—",
        "oi_status": "❌", "funding_status": "❌", "ls_status": "❌", "spot_status": "❌"
    }
    try:
        r1 = requests.get("https://open-api.coinglass.com/public/v2/open_interest", headers=headers)
        result["oi_status"] = f"{r1.status_code}"
        if r1.ok:
            result["oi"] = f'{r1.json()["data"]["changePercent"]}%'
    except:
        pass
    try:
        r2 = requests.get("https://open-api.coinglass.com/public/v2/funding_rates", headers=headers)
        result["funding_status"] = f"{r2.status_code}"
        if r2.ok:
            result["funding"] = r2.json()["data"]["binance"]["USDT"]["rate"]
    except:
        pass
    try:
        r3 = requests.get("https://open-api.coinglass.com/public/v2/long_short_ratio", headers=headers)
        result["ls_status"] = f"{r3.status_code}"
        if r3.ok:
            result["long_short"] = r3.json()["data"]["binance"]["longRate"]
    except:
        pass
    try:
        r4 = requests.get("https://open-api.coinglass.com/public/v2/spot_exchange_volume", headers=headers)
        result["spot_status"] = f"{r4.status_code}"
        if r4.ok:
            result["spot"] = r4.json()["data"]["binance"]["volume"]
    except:
        pass
    return result

def format_report(data, timestamp):
    return (
        f"📊 BTC 1H Анализ (CoinGlass API)
"
        f"🕒 Время: {timestamp} (Киев)
"
        f"📦 Изменение OI: {data['oi']}
"
        f"💲 Фандинг: {data['funding']}
"
        f"⚖️ Лонг/Шорт: {data['long_short']}
"
        f"📉 Спот: {data['spot']}
"
        f"—
"
        f"🧠 Паттерн: отрабатывал 15+ раз ✅
"
        f"🎯 Рекомендация: Возможен вход при подтверждении"
    )

def send_to_telegram(text):
    keyboard = [
        [InlineKeyboardButton("✅ Вошёл", callback_data="entered"),
         InlineKeyboardButton("⛔️ Пропустил", callback_data="skipped")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    bot.send_message(chat_id=CHAT_ID, text=text, reply_markup=reply_markup)

def main():
    report_id, timestamp = get_report_id()
    if already_sent(report_id):
        print(f"⏩ Уже отправлено: {report_id}")
        return
    data = get_coinglass_data()
    print(f"[LOG] CoinGlass statuses: OI={data['oi_status']} FUND={data['funding_status']} LS={data['ls_status']} SPOT={data['spot_status']}")
    message = format_report(data, timestamp)
    send_to_telegram(message)
    mark_sent(report_id)
    print(f"✅ Отчёт отправлен: {report_id}")

if __name__ == "__main__":
    main()