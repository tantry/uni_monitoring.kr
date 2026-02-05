#!/usr/bin/env python3
"""
Telegram message formatter for university admission alerts
"""

def format_telegram_message(title, content, url, department="general"):
    """
    Format a university admission alert for Telegram
    Returns HTML-formatted message
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
    if len(content) > 300:
        content = content[:300] + "..."
    
    # Format the message with HTML
    message = f"{emoji} <b>[새 입학 공고] {title}</b>\n\n"
    message += f"📌 <b>부서/학과</b>: {department}\n"
    
    if content:
        message += f"📝 <b>내용</b>: {content}\n"
    
    message += f"🔗 <b>링크</b>: {url}\n"
    message += f"\n#대학입시 #{department}"
    
    return message

# Legacy function name for backward compatibility
format_message = format_telegram_message

# Add this class for compatibility with multi_monitor.py
class TelegramFormatter:
    """Wrapper class for backward compatibility"""
    
    def format_message(self, title, content, url, department="general"):
        """Method that multi_monitor.py expects"""
        return format_telegram_message(title, content, url, department)
