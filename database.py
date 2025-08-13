# database.py
import sqlite3
from datetime import datetime
import os

# Full list of exactly 50 currency pairs (no crypto, indices, or commodities)
CURRENCY_PAIRS = [
    "EURUSD", "GBPUSD", "USDJPY", "USDCHF", "USDCAD", "AUDUSD", "NZDUSD",
    "EURGBP", "EURJPY", "EURCHF", "EURCAD", "EURAUD", "EURNZD",
    "GBPJPY", "GBPCHF", "GBPCAD", "GBPAUD", "GBPNZD",
    "AUDJPY", "AUDCHF", "AUDCAD", "AUDNZD",
    "NZDJPY", "NZDCHF", "NZDCAD",
    "CADJPY", "CADCHF",
    "CHFJPY",
    "EURSGD", "GBPSGD", "USDSGD", "AUDSGD", "NZDSGD", "CADSGD",
    "USDZAR", "USDTRY", "USDHKD", "USDSEK", "USDNOK", "USDDKK",
    "EURSEK", "EURNOK", "EURDKK", "GBPSEK", "GBPNOK", "GBPDKK",
    "AUDSEK", "AUDNOK", "AUDDKK", "NZDSEK"
]

DB_FILE = os.getenv("DB_FILE", "trading_data.db")


class Database:
    def __init__(self, db_file: str = DB_FILE):
        self.db_file = db_file
        self.conn = sqlite3.connect(self.db_file, check_same_thread=False)
        self.create_tables()

    def create_tables(self):
        cursor = self.conn.cursor()

        # Store incoming price data
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS market_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            symbol TEXT NOT NULL,
            timeframe TEXT NOT NULL,
            timestamp DATETIME NOT NULL,
            open REAL,
            high REAL,
            low REAL,
            close REAL,
            volume REAL
        )
        """)

        # Store generated trade signals
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS trade_signals (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            symbol TEXT NOT NULL,
            timeframe TEXT NOT NULL,
            signal_type TEXT NOT NULL, -- 'BUY' or 'SELL'
            strategy TEXT NOT NULL,    -- 'trend_reversal' or 'trend_following'
            timestamp DATETIME NOT NULL,
            confirmation TEXT           -- JSON or note about confirmation candles
        )
        """)

        # Store Telegram alerts sent
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS alerts_sent (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            symbol TEXT NOT NULL,
            timeframe TEXT NOT NULL,
            message TEXT NOT NULL,
            sent_at DATETIME NOT NULL
        )
        """)

        self.conn.commit()

    def insert_market_data(self, symbol, timeframe, timestamp, open_, high, low, close, volume):
        cursor = self.conn.cursor()
        cursor.execute("""
        INSERT INTO market_data (symbol, timeframe, timestamp, open, high, low, close, volume)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (symbol, timeframe, timestamp, open_, high, low, close, volume))
        self.conn.commit()

    def insert_trade_signal(self, symbol, timeframe, signal_type, strategy, confirmation):
        cursor = self.conn.cursor()
        cursor.execute("""
        INSERT INTO trade_signals (symbol, timeframe, signal_type, strategy, timestamp, confirmation)
        VALUES (?, ?, ?, ?, ?, ?)
        """, (symbol, timeframe, signal_type, strategy, datetime.utcnow(), confirmation))
        self.conn.commit()

    def insert_alert(self, symbol, timeframe, message):
        cursor = self.conn.cursor()
        cursor.execute("""
        INSERT INTO alerts_sent (symbol, timeframe, message, sent_at)
        VALUES (?, ?, ?, ?)
        """, (symbol, timeframe, message, datetime.utcnow()))
        self.conn.commit()

    def get_recent_market_data(self, symbol, timeframe, limit=100):
        cursor = self.conn.cursor()
        cursor.execute("""
        SELECT * FROM market_data
        WHERE symbol = ? AND timeframe = ?
        ORDER BY timestamp DESC
        LIMIT ?
        """, (symbol, timeframe, limit))
        return cursor.fetchall()

    def get_last_signal(self, symbol, timeframe):
        cursor = self.conn.cursor()
        cursor.execute("""
        SELECT * FROM trade_signals
        WHERE symbol = ? AND timeframe = ?
        ORDER BY timestamp DESC
        LIMIT 1
        """, (symbol, timeframe))
        return cursor.fetchone()

    def close(self):
        self.conn.close()


# Example usage
if __name__ == "__main__":
    db = Database()
    db.insert_market_data("EURUSD", "5m", datetime.utcnow(), 1.1000, 1.1020, 1.0990, 1.1010, 1500)
    db.insert_trade_signal("EURUSD", "5m", "BUY", "trend_reversal", '{"pattern": "3-candle"}')
    db.insert_alert("EURUSD", "5m", "BUY signal confirmed")
    print(db.get_recent_market_data("EURUSD", "5m"))
    db.close()
