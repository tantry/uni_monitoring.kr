# test_telegram.py - Test Telegram formatting
"""
ONLY run this if you want to test with actual Telegram bot
Requires: python-telegram-bot package
"""

import asyncio
import sys

try:
    from telegram import Bot
except ImportError:
    print("❌ python-telegram-bot not installed.")
    print("Install with: pip install python-telegram-bot")
    sys.exit(1)

# Replace with your actual token and chat ID
TELEGRAM_TOKEN = "YOUR_BOT_TOKEN_HERE"
CHAT_ID = "YOUR_CHAT_ID_HERE"

async def send_test():
    if TELEGRAM_TOKEN == "YOUR_BOT_TOKEN_HERE":
        print("❌ Please add your Telegram bot token first!")
        return
    
    bot = Bot(token=TELEGRAM_TOKEN)
    
    test_message = (
        "🎵 **테스트 알림**\n\n"
        "📘 **진학사** `[JIN]` | 서울대학교\n"
        "🎸 🎤 **실용음악 • 보컬전문**\n"
        "• 재즈보컬 추가모집 (R&B 포함)\n"
        "• 마감: 2024.12.20\n"
        "• [🔗 보기](https://example.com)\n\n"
        "📗 **Uway** `[UWAY]` | 경기대학교\n"
        "🎻 **클래식**\n"
        "• 성악 추가모집\n"
        "• 마감: 2024.12.18\n"
        "• [🔗 보기](https://example.com)"
    )
    
    try:
        await bot.send_message(
            chat_id=CHAT_ID,
            text=test_message,
            parse_mode='Markdown'
        )
        print("✅ 테스트 메시지 전송 완료!")
    except Exception as e:
        print(f"❌ 오류: {e}")

if __name__ == "__main__":
    asyncio.run(send_test())
