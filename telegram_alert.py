# telegram_alert.py

import requests
from datetime import datetime

# Your actual Telegram bot token and chat ID
BOT_TOKEN = "8393216803:AAGeejYBbXRMgKrp3zv8ifAxnOgYNMVZUBw"
CHAT_ID = "6005165491"

def send_telegram_signal(symbol, signal_type, timeframe):
    """
    Sends a formatted signal message to Telegram.

    Args:
        symbol (str): e.g., "EUR/USD"
        signal_type (str): "BUY" or "SELL"
        timeframe (str): e.g., "1min", "3min"
    """
    now = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')
    message = (
        f"🚨 *Trading Signal Alert* 🚨\n\n"
        f"📈 *Pair:* {symbol}\n"
        f"⏱️ *Timeframe:* {timeframe}\n"
        f"📊 *Signal:* *{signal_type.upper()}*\n"
        f"🕒 *Time:* {now}"
    )
    
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": message,
        "parse_mode": "Markdown"
    }

    try:
        response = requests.post(url, data=payload)
        response.raise_for_status()
        print(f"[INFO] Telegram alert sent for {symbol} ({timeframe}) - {signal_type}")
    except requests.exceptions.RequestException as e:
        print(f"[ERROR] Failed to send Telegram alert: {e}")
