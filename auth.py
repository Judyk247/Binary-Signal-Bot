# auth.py
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Telegram bot credentials
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

# Optional: sanity checks
if not TELEGRAM_BOT_TOKEN:
    raise ValueError("Missing TELEGRAM_BOT_TOKEN in .env file")
if not TELEGRAM_CHAT_ID:
    raise ValueError("Missing TELEGRAM_CHAT_ID in .env file")
