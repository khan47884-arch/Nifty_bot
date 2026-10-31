import requests, os
BOT = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT = os.getenv("TELEGRAM_CHAT_ID")
url = f"https://api.telegram.org/bot{BOT}/sendMessage"
requests.post(url, data={"chat_id": CHAT, "text": "💎 TEST - Bot zinda hai!"}, timeout=20)
