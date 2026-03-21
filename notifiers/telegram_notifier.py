import logging
import requests
from typing import Optional

class TelegramNotifier:
    def __init__(self, config: dict):
        self.bot_token = config.get('bot_token', '')
        self.chat_id = config.get('chat_id', '')
        self.logger = logging.getLogger(__name__)
    
    def send_message(self, message: str, parse_mode: str = "HTML") -> bool:
        """Send message to Telegram with rate limit handling"""
        if not self.bot_token or not self.chat_id:
            self.logger.error("Telegram credentials not configured")
            return False
        
        import time
        
        def _send():
            url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"
            payload = {
                'chat_id': self.chat_id,
                'text': message,
                'parse_mode': parse_mode,
                'disable_web_page_preview': False
            }
            return requests.post(url, json=payload, timeout=10)
        
        try:
            # First attempt
            response = _send()
            
            if response.status_code == 200:
                self.logger.debug("Message sent successfully")
                time.sleep(0.5)  # Delay between messages
                return True
                
            elif response.status_code == 429:
                # Rate limited - parse retry time and wait
                try:
                    data = response.json()
                    retry_after = data.get('parameters', {}).get('retry_after', 15)
                    self.logger.warning(f"Rate limited. Waiting {retry_after} seconds...")
                    time.sleep(retry_after + 1)
                    
                    # Retry once
                    response2 = _send()
                    if response2.status_code == 200:
                        self.logger.info("Message sent after rate limit wait")
                        time.sleep(0.5)
                        return True
                    else:
                        self.logger.error(f"Retry failed: {response2.status_code}")
                        return False
                        
                except Exception as e:
                    self.logger.error(f"Error handling rate limit: {e}")
                    time.sleep(15)  # Fallback wait
                    return False
            else:
                self.logger.error(f"Failed to send: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            self.logger.error(f"Error sending Telegram message: {e}")
            return False
    
    def test_connection(self) -> bool:
        """Test Telegram bot connection"""
        try:
            url = f"https://api.telegram.org/bot{self.bot_token}/getMe"
            response = requests.get(url, timeout=5)
            return response.status_code == 200
        except:
            return False
