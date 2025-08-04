import requests

TELEGRAM_TOKEN = '8393216803:AAGeejYBbXRMgKrp3zv8ifAxnOgYNMVZUBw'
CHAT_ID = '6005165491'

def send_telegram_message(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": message
    }
    response = requests.post(url, data=payload)
    print("Status code:", response.status_code)
    print("Response:", response.text)

print("Sending test message...")
send_telegram_message("✅ Your bot is live on GitHub!")
print("Done.")
