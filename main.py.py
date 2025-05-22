import asyncio
import aiohttp
import certifi
import ssl
import os
from datetime import datetime, timezone, timedelta
from telegram import Bot

COINGLASS_API_KEY = os.getenv("COINGLASS_API_KEY", "66fbafd2a182492f8442cfb465b39027")
TELEGRAM_BOT_TOKEN = os.getenv("TOKEN", "7889272376:AAHQDW6esj8312M_pfqj6zrcF4XlkC1OA4")
TELEGRAM_CHAT_ID = os.getenv("CHAT_ID", "5634238573")

ssl_context = ssl.create_default_context(cafile=certifi.where())
LAST_REPORT_FILE = 'last_report.txt'

async def fetch_data(session, url, params=None):
    headers = {'coinglassSecret': COINGLASS_API_KEY}
    async with session.get(url, headers=headers, params=params, ssl=ssl_context) as resp:
        return await resp.json()

async def generate_report():
    async with aiohttp.ClientSession() as session:
        symbol = 'BTC'
        report = "=== Binance BTC Report ===\n\n"

        endpoints = {
            'Open Interest': 'https://open-api.coinglass.com/public/v2/open_interest',
            'Funding Rate': 'https://open-api.coinglass.com/public/v2/funding_rate',
            'Long/Short Ratio': 'https://open-api.coinglass.com/public/v2/long_short_account',
            'Liquidations': 'https://open-api.coinglass.com/public/v2/liquidation',
            'Spot Volume': 'https://open-api.coinglass.com/public/v2/spot_exchange_volume',
            'Perpetual Futures Volume': 'https://open-api.coinglass.com/public/v2/futures_volume',
            'Top Traders Ratio': 'https://open-api.coinglass.com/public/v2/top_account_ratio',
        }

        for label, url in endpoints.items():
            data = await fetch_data(session, url, {'symbol': symbol})
            if data and 'data' in data:
                for item in data['data']:
                    if item.get('exchangeName', '').lower() == 'binance':
                        value = (
                            item.get('value') or
                            item.get('fundingRate') or
                            item.get('totalVolUsd') or
                            item.get('longAccount') or
                            item
                        )
                        report += f"{label}: {value}\n"
                        break

        return report.strip()

def read_last_report():
    if os.path.exists(LAST_REPORT_FILE):
        with open(LAST_REPORT_FILE, 'r', encoding='utf-8') as f:
            return f.read()
    return ""

def save_last_report(report):
    with open(LAST_REPORT_FILE, 'w', encoding='utf-8') as f:
        f.write(report)

async def send_to_telegram(message):
    bot = Bot(token=TELEGRAM_BOT_TOKEN)
    await bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=message[:4096])

async def main():
    try:
        report = await generate_report()
        last_report = read_last_report()

        if report == last_report:
            print("Данные не изменились. Отчёт не отправлен.")
        else:
            await send_to_telegram(report)
            save_last_report(report)
            print("Новый отчёт отправлен.")
    except Exception as e:
        print("Ошибка:", e)

if __name__ == '__main__':
    asyncio.run(main())
