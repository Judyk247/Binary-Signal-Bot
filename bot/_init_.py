# bot/__init__.py

# Flask app secret key
SECRET_KEY = "3206fe46111a9445c295b54e0dff2ad437cb6d706b9e8fd227939a403a918ffc"

# Admin credentials
ADMIN_USERNAME = "JUDYK"
ADMIN_PASSWORD = "Engr.Jude247"

# Email credentials
EMAIL_SENDER = "judykengineeringltd@gmail.com"
EMAIL_PASSWORD = "Engr.Jude247"
EMAIL_RECEIVER = "judykengineeringltd@gmail.com"  # You can change if needed

# Telegram bot credentials
TELEGRAM_BOT_TOKEN = "8393216803:AAGeejYBbXRMgKrp3zv8ifAxnOgYNMVZUBw"
CHAT_ID = "6005165491"

# API keys
TWELVE_DATA_API_KEY = "c1516b63b0e54828bc83861b9676501f"

# Optional bot import
try:
    from .telegram_bot import start_bot
except ImportError:
    start_bot = None

__all__ = [
    "SECRET_KEY",
    "ADMIN_USERNAME",
    "ADMIN_PASSWORD",
    "EMAIL_SENDER",
    "EMAIL_PASSWORD",
    "EMAIL_RECEIVER",
    "TELEGRAM_BOT_TOKEN",
    "CHAT_ID",
    "TWELVE_DATA_API_KEY",
    "start_bot",
]
