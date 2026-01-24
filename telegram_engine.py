import requests
from config import TELEGRAM_BOT_TOKEN


def send_telegram(chat_id, message):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"

    payload = {
        "chat_id": chat_id,
        "text": message
    }

    r = requests.post(url, json=payload)

    if r.status_code != 200:
        print("Telegram Error:", r.text)
