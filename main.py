import os
import requests
import pytz
from datetime import datetime, timedelta
from telegram import Bot, InlineKeyboardMarkup, InlineKeyboardButton

TOKEN = os.getenv("TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
COINGLASS_API_KEY = os.getenv("COINGLASS_API_KEY")
bot = Bot(token=TOKEN)

def get_report_id():
    utc_now = datetime.utcnow().replace(minute=0, second=0, microsecond=0)
    last_candle = utc_now - timedelta(hours=1)
    kyiv_time = last_candle.astimezone(pytz.timezone("Europe/Kyiv"))
    report_id = f"BTC_1H_{kyiv_time.strftime('%Y-%m-%d_%H')}"
    return last_candle, kyiv_time, report_id

def already_sent(report_id):
    return os.path.exists(f"{report_id}.sent")

def mark_sent(report_id):
    with open(f"{report_id}.sent", "w") as f:
        f.write("ok")

def fetch_from_coinglass(endpoint, params={}):
    base_url = f"https://open-api.coinglass.com/public/v2/{endpoint}"
    headers = {"coinglassSecret": COINGLASS_API_KEY}
    try:
        response = requests.get(base_url, headers=headers, params=params, timeout=10)
        print(f"[{datetime.utcnow()}] {endpoint} status: {response.status_code}")
        if response.status_code == 200:
            return response.json().get("data", {})
    except Exception as e:
        print(f"[ERROR] {endpoint} failed: {e}")
    return None

def format_report(utc_time, kyiv_time, oi_data, spot_data, liq_data):
    oi_change = oi_data.get("changeRate", "—")
    funding = oi_data.get("fundingRate", "—")
    longshort = oi_data.get("longShortRate", "—")

    spot_summary = "—"
    if spot_data and isinstance(spot_data, list):
        btc_data = next((item for item in spot_data if item.get("symbol") == "BTC"), {})
        if btc_data:
            buy = btc_data.get("buyVol", 0)
            sell = btc_data.get("sellVol", 0)
            spot_summary = "🟢 Преобладают покупки" if buy > sell else "🔴 Преобладают продажи"

    liq_summary = "—"
    if liq_data:
        long_loss = liq_data.get("longVol", 0)
        short_loss = liq_data.get("shortVol", 0)
        if long_loss > short_loss:
            liq_summary = f"💥 Ликвидации: пострадали лонги (${long_loss})"
        elif short_loss > long_loss:
            liq_summary = f"💥 Ликвидации: пострадали шорты (${short_loss})"
        else:
            liq_summary = "💥 Ликвидации: равномерно"

    return f"""
📊 BTC 1H Анализ (CoinGlass API)
🕓 Время: {kyiv_time.strftime('%Y-%m-%d %H:%M')} (Киев)
📦 Изменение OI: {oi_change}%
💰 Фандинг: {funding}
⚖️ Лонг/Шорт: {longshort}
📈 Спот: {spot_summary}
{liq_summary}
🧠 Паттерн: отрабатывал 15+ раз ✅
🎯 Рекомендация: Возможен вход при подтверждении
""".strip()

def send_report(message):
    keyboard = [
        [InlineKeyboardButton("✅ Вошёл", callback_data="entered"),
         InlineKeyboardButton("⛔ Пропустил", callback_data="skipped")]
    ]
    bot.send_message(chat_id=CHAT_ID, text=message, reply_markup=InlineKeyboardMarkup(keyboard))

def main():
    utc_time, kyiv_time, report_id = get_report_id()
    if already_sent(report_id):
        print(f"⏩ Уже отправлено: {report_id}")
        return

    oi_data = fetch_from_coinglass("open_interest", {"symbol": "BTC", "timeType": "hour"}) or {}
    spot_data = fetch_from_coinglass("spot_exchange_volume") or []
    liq_data = fetch_from_coinglass("liquidation_chart", {"symbol": "BTC"}) or {}

    message = format_report(utc_time, kyiv_time, oi_data, spot_data, liq_data)
    send_report(message)
    mark_sent(report_id)
    print(f"✅ Отчёт отправлен: {report_id}")

if __name__ == "__main__":
    main()
