import requests, os
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
print(f"Token exists: {bool(BOT_TOKEN)}")
print(f"Chat exists: {bool(CHAT_ID)}")
url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
r = requests.post(url, data={"chat_id": CHAT_ID, "text": "🎩 BOND 007 TEST - Bot working! Telegram connected ✅"})
print(r.text)
