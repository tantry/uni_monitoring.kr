#!/usr/bin/env python3
"""
Telegram message formatter for university admission alerts
UPDATED for robust architecture compatibility
"""
import requests
import sys
import os

# Add current directory to path for config import
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Try to import Telegram config
try:
    from config import BOT_TOKEN, CHAT_ID
    HAS_TELEGRAM_CONFIG = True
except ImportError:
    HAS_TELEGRAM_CONFIG = False
    BOT_TOKEN = None
    CHAT_ID = None


def format_telegram_message(title, content, url, department="general"):
    """
    Format a university admission alert for Telegram
    Returns HTML-formatted message
    
    Args:
        title: Article title
        content: Article content
        url: Article URL
        department: Department identifier
    
    Returns:
        HTML-formatted Telegram message
    """
    # Department emoji mapping
    department_emojis = {
        'music': '🎵',
        'korean': '📚', 
        'english': '🔤',
        'liberal': '📖',
        'general': '🎓'
    }
    
    emoji = department_emojis.get(department, '🎓')
    
    # Truncate content if too long (Telegram has limits)
    if content and len(content) > 300:
        content = content[:300] + "..."
    
    # Format the message with HTML
    message = f"{emoji} <b>[새 입학 공고] {title}</b>\n\n"
    
    # Add department if not general
    if department != 'general':
        message += f"📌 <b>부서/학과</b>: {department}\n"
    
    if content:
        message += f"📝 <b>내용</b>: {content}\n"
    
    message += f"🔗 <b>링크</b>: {url}\n"
    
    # Add hashtags
    message += f"\n#대학입시"
    if department != 'general':
        message += f" #{department}"
    
    return message


def format_program(program_data):
    """
    Format program data for Telegram (compatibility with new architecture)
    
    Args:
        program_data: Dictionary with program/article data
    
    Returns:
        Formatted Telegram message
    """
    # Extract data from program dictionary
    title = program_data.get('title', 'No Title')
    content = program_data.get('content', '')
    url = program_data.get('url', '')
    
    # Extract department - handle both string and nested dictionary
    department = program_data.get('department', 'general')
    if isinstance(department, dict):
        department = department.get('name', 'general')
    
    return format_telegram_message(title, content, url, department)


def send_telegram_message(message, parse_mode="HTML"):
    """
    Send a message to Telegram channel
    
    Args:
        message: Message text to send
        parse_mode: Telegram parse mode (HTML, Markdown, etc.)
    
    Returns:
        True if sent successfully, False otherwise
    """
    if not HAS_TELEGRAM_CONFIG:
        print("⚠ Telegram config not available")
        return False
    
    if not BOT_TOKEN or not CHAT_ID:
        print("⚠ Telegram credentials not set")
        return False
    
    try:
        # Telegram Bot API URL
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        
        # Request payload
        payload = {
            "chat_id": CHAT_ID,
            "text": message,
            "parse_mode": parse_mode,
            "disable_web_page_preview": False
        }
        
        # Send request
        response = requests.post(url, json=payload, timeout=10)
        
        if response.status_code == 200:
            print(f"✅ Telegram message sent successfully")
            return True
        else:
            print(f"❌ Telegram API error: {response.status_code} - {response.text}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Telegram request error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected Telegram error: {e}")
        return False


# Legacy function name for backward compatibility
format_message = format_telegram_message


class TelegramFormatter:
    """
    Formatter class for backward compatibility with multi_monitor.py
    
    multi_monitor.py expects:
    1. self.formatter.format_program(program)
    2. send_telegram_message() function (available globally)
    """
    
    def __init__(self):
        """Initialize formatter"""
        pass
    
    def format_message(self, title, content, url, department="general"):
        """Legacy method that some code might expect"""
        return format_telegram_message(title, content, url, department)
    
    def format_program(self, program_data):
        """Method that multi_monitor.py expects for new architecture"""
        return format_program(program_data)


# Test function
def test_telegram_integration():
    """Test Telegram formatter and sender"""
    print("Testing Telegram Integration...")
    print("=" * 50)
    
    # Test 1: Formatter functions
    print("\n1. Testing formatter functions:")
    
    test_article = {
        'title': '서울대학교 음악학과 추가모집 공고',
        'content': '서울대학교 음악학과에서 2026학년도 추가모집을 실시합니다.',
        'url': 'https://adiga.kr/ArticleDetail.do?articleID=26546',
        'department': 'music'
    }
    
    # Test format_program
    message = format_program(test_article)
    print(f"✅ format_program() works")
    print(f"Message preview: {message[:80]}...")
    
    # Test 2: TelegramFormatter class
    print("\n2. Testing TelegramFormatter class:")
    formatter = TelegramFormatter()
    message2 = formatter.format_program(test_article)
    print(f"✅ formatter.format_program() works")
    
    # Test 3: Send function (test mode - won't actually send)
    print("\n3. Testing send_telegram_message (test mode):")
    if HAS_TELEGRAM_CONFIG:
        print(f"✅ BOT_TOKEN: {'*' * 10}{BOT_TOKEN[-5:] if BOT_TOKEN else 'NOT SET'}")
        print(f"✅ CHAT_ID: {CHAT_ID}")
        
        # Test send function but don't actually send
        print("   (Send function available - will send if called)")
    else:
        print("⚠ Telegram config not loaded")
    
    print("\n" + "=" * 50)
    print("Telegram formatter updated successfully!")
    print("\nFeatures added:")
    print("1. format_program() for new architecture compatibility")
    print("2. send_telegram_message() function")
    print("3. Enhanced TelegramFormatter class")
    print("4. Department extraction from program data")
    print("5. Error handling and logging")


if __name__ == "__main__":
    test_telegram_integration()
