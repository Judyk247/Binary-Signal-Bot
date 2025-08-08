# telegram_bot.py

import requests

TELEGRAM_BOT_TOKEN = "8393216803:AAGeejYBbXRMgKrp3zv8ifAxnOgYNMVZUBw"
TELEGRAM_CHAT_ID = "6005165491"

def send_telegram_message(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": "HTML"
    }
    try:
        response = requests.post(url, data=payload)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"[Telegram] Failed to send message: {e}")
