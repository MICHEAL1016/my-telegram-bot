import requests

BOT_TOKEN = "8045488551:AAGhNuWrM7KTdKvh3NKS2svwqFufMSSB_r8"
WEBHOOK_URL = "https://smooth-our-strings-buithanhluan290.replit.app/telegram"  # Update this if your Flask endpoint is different

url = f"https://api.telegram.org/bot{BOT_TOKEN}/setWebhook"
resp = requests.post(url, data={"url": WEBHOOK_URL})
print(resp.json())
