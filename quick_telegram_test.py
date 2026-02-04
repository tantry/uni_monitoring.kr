# quick_telegram_test.py
import config
import requests

bot_token = config.BOT_TOKEN
channel_id = config.CHANNEL_ID

print(f"BOT_TOKEN: {bot_token[:10]}...")
print(f"CHANNEL_ID: {channel_id}")

url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
data = {
    'chat_id': channel_id,
    'text': 'Test from University Monitor'
}

response = requests.post(url, data=data)
print(f"Status: {response.status_code}")
print(f"Response: {response.text}")
