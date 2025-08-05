import requests
import time
from datetime import datetime
import os
from dotenv import load_dotenv

# Load environment variables from the .env file
load_dotenv()

# Directly assign your values (already filled in for you)
TELEGRAM_TOKEN = "8393216803:AAGeejYBbXRMgKrp3zv8ifAxnOgYNMVZUBw"
CHAT_ID = "6005165491"
API_KEY = "bcbbfc38a4b24af1b800bfda29654162"

# Optional: Print to verify (remove this later in production)
print("TELEGRAM_TOKEN:", TELEGRAM_TOKEN)
print("CHAT_ID:", CHAT_ID)
print("API_KEY:", API_KEY)
# List of 12 common currency pairs and cryptos
symbols = [
    "EUR/USD", "GBP/USD", "USD/JPY", "USD/CHF",
    "AUD/USD", "USD/CAD", "NZD/USD", "BTC/USD",
    "ETH/USD", "LTC/USD", "XRP/USD", "BNB/USD"
]

# Bot scan interval (seconds)
INTERVAL = 180  # 3 minutes

def send_telegram_alert(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    data = {
        "chat_id": CHAT_ID,
        "text": message
    }
    requests.post(url, data=data)

def get_indicator_data(symbol):
    base_url = "https://api.twelvedata.com"
    
    params = {
        "symbol": symbol,
        "interval": "3min",
        "outputsize": 50,
        "apikey": API_KEY
    }

    # EMA
    ema_url = f"{base_url}/ema"
    ema_params = {**params, "time_period": 150}
    ema = requests.get(ema_url, params=ema_params).json()

    # Stochastic
    sto_url = f"{base_url}/stochastic"
    sto_params = {**params, "time_period": 14, "slow_k": 3, "slow_d": 3}
    stochastic = requests.get(sto_url, params=sto_params).json()

    # Alligator
    alligator = {
        "jaw": requests.get(f"{base_url}/smma", params={**params, "time_period": 13}).json(),
        "teeth": requests.get(f"{base_url}/smma", params={**params, "time_period": 8}).json(),
        "lips": requests.get(f"{base_url}/smma", params={**params, "time_period": 5}).json()
    }

    # Price
    price_url = f"{base_url}/time_series"
    price_params = {**params}
    price = requests.get(price_url, params=price_params).json()

    return ema, stochastic, alligator, price

def analyze_and_alert():
    for symbol in symbols:
        try:
            ema, stochastic, alligator, price_data = get_indicator_data(symbol)

            if "values" not in price_data:
                continue

            candles = price_data["values"]
            last_close = float(candles[0]["close"])
            prev_close = float(candles[1]["close"])

            ema_value = float(ema["values"][0]["ema"])
            k = float(stochastic["values"][0]["slow_k"])
            d = float(stochastic["values"][0]["slow_d"])

            jaw = float(alligator["jaw"]["values"][0]["smma"])
            teeth = float(alligator["teeth"]["values"][0]["smma"])
            lips = float(alligator["lips"]["values"][0]["smma"])

            # Define momentum candles
            bullish_momentum = last_close > prev_close and (last_close - prev_close) > 0.1
            bearish_momentum = last_close < prev_close and (prev_close - last_close) > 0.1

            now = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")

            # Buy Conditions
            if last_close > ema_value and last_close > jaw and last_close > teeth and last_close > lips:
                if bullish_momentum and k > 30 and k > d:
                    msg = f"📈 BUY SIGNAL\nPair: {symbol}\nTime: {now} UTC\nPrice above EMA & Alligator\nStochastic: {round(k, 2)}"
                    send_telegram_alert(msg)
                elif k > 30 and lips < last_close and last_close > jaw:
                    msg = f"📈 BUY SIGNAL\nPair: {symbol}\nTime: {now} UTC\nCrossed Alligator Up\nStochastic: {round(k, 2)}"
                    send_telegram_alert(msg)

            # Sell Conditions
            if last_close < ema_value and last_close < jaw and last_close < teeth and last_close < lips:
                if bearish_momentum and k < 80 and k < d:
                    msg = f"📉 SELL SIGNAL\nPair: {symbol}\nTime: {now} UTC\nPrice below EMA & Alligator\nStochastic: {round(k, 2)}"
                    send_telegram_alert(msg)
                elif k < 80 and lips > last_close and last_close < jaw:
                    msg = f"📉 SELL SIGNAL\nPair: {symbol}\nTime: {now} UTC\nCrossed Alligator Down\nStochastic: {round(k, 2)}"
                    send_telegram_alert(msg)

        except Exception as e:
            print(f"Error on {symbol}: {e}")

def main():
    while True:
        analyze_and_alert()
        time.sleep(INTERVAL)

if __name__ == "__main__":
    main()
