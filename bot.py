# PostBot.py

import requests
from datetime import datetime

TELEGRAM_BOT_TOKEN = "8393216803:AAGeejYBbXRMgKrp3zv8ifAxnOgYNMVZUBw"
TELEGRAM_CHAT_ID = "6005165491"

def send_signal_to_telegram(symbol, direction, timeframe):
    """
    Sends a trade signal message to your Telegram bot.
    """
    now = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
    message = (
        f"🚨 *Trade Signal Alert*\n"
        f"Symbol: `{symbol}`\n"
        f"Direction: *{direction}*\n"
        f"Timeframe: `{timeframe}`\n"
        f"Time: {now}"
    )

    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": "Markdown"
    }

    try:
        response = requests.post(url, data=payload)
        response.raise_for_status()
    except Exception as e:
        print(f"Failed to send signal to Telegram: {e}")
