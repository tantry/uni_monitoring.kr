#!/usr/bin/env python3
"""
Send a test Telegram message
"""
import requests
import config
from telegram_formatter import TelegramFormatter

formatter = TelegramFormatter()

# Create a test article
test_article = {
    'title': '[테스트] 서울대학교 음악학과 추가모집 공고',
    'content': '서울대학교 음악학과에서 2026학년도 추가모집을 실시합니다.',
    'url': 'https://adiga.kr/ArticleDetail.do?articleID=99999'
}

message = formatter.format_message(
    test_article['title'],
    test_article['content'], 
    test_article['url'],
    'music'
)

print(f"📤 Sending test message...")
print(f"Message preview: {message[:100]}...")

url = f"https://api.telegram.org/bot{config.BOT_TOKEN}/sendMessage"
payload = {
    'chat_id': config.CHAT_ID,
    'text': message,
    'parse_mode': 'HTML'
}

response = requests.post(url, json=payload, timeout=10)
if response.status_code == 200:
    print("✅ Test message sent to Telegram!")
else:
    print(f"❌ Failed: {response.status_code} - {response.text}")
