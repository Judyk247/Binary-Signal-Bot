# config.py

# Telegram Bot Config
TELEGRAM_BOT_TOKEN = '8393216803:AAGeejYBbXRMgKrp3zv8ifAxnOgYNMVZUBw'
TELEGRAM_CHAT_ID = '6005165491'

# Twelve Data API Key
TWELVE_DATA_API_KEY = 'c1516b63b0e54828bc83861b9676501f'

# Admin Login Credentials
ADMIN_USERNAME = 'JUDYK'
ADMIN_PASSWORD = 'Engr.Jude247'

# Email Alert Config (prepared, but currently inactive)
EMAIL_NOTIFICATIONS_ENABLED = False
EMAIL_SENDER = 'your_gmail@gmail.com'  # Not active yet
EMAIL_PASSWORD = 'your_app_password'   # Not active yet
EMAIL_RECEIVER = 'your_email@gmail.com'  # Not active yet

# Symbols to scan (30 common currency pairs)
SYMBOLS_TO_SCAN = [
    'EUR/USD', 'GBP/USD', 'USD/JPY', 'USD/CHF', 'AUD/USD',
    'USD/CAD', 'NZD/USD', 'EUR/GBP', 'EUR/JPY', 'GBP/JPY',
    'AUD/JPY', 'CHF/JPY', 'EUR/AUD', 'GBP/AUD', 'AUD/CAD',
    'NZD/JPY', 'EUR/CAD', 'GBP/CAD', 'USD/SGD', 'USD/HKD',
    'USD/SEK', 'USD/NOK', 'USD/MXN', 'USD/ZAR', 'EUR/CHF',
    'EUR/NZD', 'GBP/NZD', 'AUD/NZD', 'NZD/CHF', 'CAD/JPY'
]

# Timeframes to scan
TIMEFRAMES = ['1min', '2min', '3min', '5min']

# Candle Analysis Parameters
CANDLES_TO_ANALYZE = 50  # Analyze last 50 candles for pattern recognition

# Signal Strategy Parameters
STOCH_OVERBOUGHT = 70
STOCH_OVERSOLD = 30
EMA_PERIOD = 150
ALLIGATOR_JAW = 13
ALLIGATOR_TEETH = 8
ALLIGATOR_LIPS = 5
STOCH_K = 14
STOCH_D = 3
STOCH_SLOWING = 3
