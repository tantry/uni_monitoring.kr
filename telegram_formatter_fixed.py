#!/usr/bin/env python3
"""
Telegram message formatter for university admission alerts
FIXED: Proper HTML escaping for Telegram
"""
import requests
import sys
import os
import html

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


def escape_html(text):
    """
    Escape HTML special characters for Telegram
    
    Telegram requires &, <, > to be escaped in HTML mode
    """
    if not text:
        return ""
    # Escape basic HTML entities
    text = html.escape(text)
    # Telegram also doesn't like certain characters in HTML mode
    # Replace common problematic characters
    text = text.replace('"', '&quot;')
    text = text.replace("'", '&apos;')
    return text


def format_telegram_message(title, content, url, department="general"):
    """
    Format a university admission alert for Telegram
    Returns HTML-formatted message with proper escaping
    
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
    
    # Escape all text for HTML
    safe_title = escape_html(title)
    safe_content = escape_html(content)
    safe_url = escape_html(url)
    
    # Truncate content if too long (Telegram has limits)
    if safe_content and len(safe_content) > 300:
        safe_content = safe_content[:300] + "..."
    
    # Format the message with HTML - use safe/escaped text
    message = f"{emoji} <b>[새 입학 공고] {safe_title}</b>\n\n"
    
    # Add department if not general
    if department != 'general':
        safe_department = escape_html(department)
        message += f"📌 <b>부서/학과</b>: {safe_department}\n"
    
    if safe_content:
        message += f"📝 <b>내용</b>: {safe_content}\n"
    
    message += f"🔗 <b>링크</b>: {safe_url}\n"
    
    # Add hashtags (no escaping needed for hashtags)
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


# Test the fix
if __name__ == "__main__":
    print("Testing HTML escaping fix...")
    
    # Test with problematic text that caused the error
    test_cases = [
        {
            'title': '[ebs뉴스 2026-02-03 발췌] 서울대학교 음악학과',
            'content': 'EBS 뉴스에서 발췌한 내용 <특별기획> "2026학년도" 입시',
            'url': 'https://adiga.kr/ArticleDetail.do?articleID=26546',
            'department': 'music'
        },
        {
            'title': 'Normal title without special chars',
            'content': 'Normal content',
            'url': 'https://example.com',
            'department': 'general'
        }
    ]
    
    for i, test in enumerate(test_cases, 1):
        print(f"\nTest {i}:")
        print(f"  Title: {test['title']}")
        message = format_telegram_message(**test)
        print(f"  Formatted message (first 100 chars):")
        print(f"  {message[:100]}...")
    
    print("\n✅ HTML escaping fix ready")
