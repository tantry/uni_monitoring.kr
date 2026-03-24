import logging
import requests
import time
from typing import Optional

class TelegramNotifier:
    def __init__(self, config: dict):
        self.bot_token = config.get('bot_token', '')
        self.group_id = config.get('group_id', '')  # Changed from chat_id
        self.topics = config.get('topics', {})
        self.department_mapping = config.get('department_mapping', {})
        self.default_topic = config.get('default_topic', 'jobs_general')
        self.logger = logging.getLogger(__name__)
    
    def _get_topic_id(self, department: str) -> Optional[int]:
        """Get topic thread ID for a department"""
        if not department:
            return self.topics.get(self.default_topic)
        
        department_lower = department.lower()
        
        # Check mapping
        topic_name = self.department_mapping.get(department_lower)
        if topic_name:
            self.logger.debug(f"Mapping {department_lower} -> topic {topic_name}, ID: {self.topics.get(topic_name)}")
            return self.topics.get(topic_name)
        else:
            self.logger.debug(f"No mapping found for {department_lower}")
        
        # Direct match
        if department_lower in self.topics:
            return self.topics[department_lower]
        
        # Default
        return self.topics.get(self.default_topic)
    
    def send_message(self, message: str, department: str = None, parse_mode: str = "HTML") -> bool:
        """Send message to Telegram group, optionally to a specific topic"""
        if not self.bot_token or not self.group_id:
            self.logger.error("Telegram credentials not configured")
            return False
        
        # Get topic ID if department provided
        topic_id = None
        if department:
            topic_id = self._get_topic_id(department)
        
        url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"
        payload = {
            'chat_id': self.group_id,
            'text': message,
            'parse_mode': parse_mode,
            'disable_web_page_preview': False
        }
        
        if topic_id:
            payload['message_thread_id'] = topic_id
        
        try:
            response = requests.post(url, json=payload, timeout=10)
            time.sleep(0.5)
            
            if response.status_code == 200:
                self.logger.debug("Message sent successfully")
                return True
                
            elif response.status_code == 429:
                data = response.json()
                retry_after = data.get('parameters', {}).get('retry_after', 15)
                self.logger.warning(f"Rate limited. Waiting {retry_after} seconds...")
                time.sleep(retry_after + 1)
                
                response2 = requests.post(url, json=payload, timeout=10)
                if response2.status_code == 200:
                    self.logger.info("Message sent after rate limit wait")
                    return True
                else:
                    self.logger.error(f"Retry failed: {response2.status_code}")
                    return False
            else:
                self.logger.error(f"Failed to send: {response.status_code}")
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
