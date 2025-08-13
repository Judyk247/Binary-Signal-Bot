# config.py
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Telegram settings
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

# Trading settings
CURRENCY_PAIRS = [
    "EURUSD", "GBPUSD", "USDJPY", "AUDUSD", "USDCAD",
    "USDCHF", "NZDUSD", "EURGBP", "EURJPY", "GBPJPY",
    "AUDJPY", "CADJPY", "CHFJPY", "EURAUD", "EURCAD",
    "EURCHF", "GBPAUD", "GBPCAD", "GBPCHF", "GBPNZD",
    "AUDCAD", "AUDCHF", "AUDNZD", "CADCHF", "NZDCAD",
    "NZDCHF", "NZDJPY", "USDNOK", "USDSEK", "USDDKK",
    "USDZAR", "USDMXN", "USDTRY", "USDHKD", "USDHUF",
    "USDPLN", "EURSEK", "EURNOK", "EURTRY", "EURZAR",
    "GBPSEK", "GBPNOK", "GBPTRY", "AUDSGD", "NZDSGD",
    "USDSGD", "SGDJPY", "HKDJPY", "TRYJPY", "ZARJPY"
]

# Timeframes mapping
TIMEFRAMES = {
    "trend_reversal": "5m",
    "trend_following": ["1m", "2m", "3m"]
}

# Strategy parameters
EMA_PERIOD = 150
STOCH_SETTINGS = (14, 3, 3)
ALLIGATOR_SETTINGS = {
    "jaw": 15,
    "teeth": 8,
    "lips": 5
}
ATR_PERIOD = 14
ATR_LOOKBACK = 50
