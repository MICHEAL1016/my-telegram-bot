import requests
import os
from dotenv import load_dotenv; load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
r = requests.get(f"https://api.telegram.org/bot{BOT_TOKEN}/getWebhookInfo")
print(r.json())
