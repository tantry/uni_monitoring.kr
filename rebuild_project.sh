#!/bin/bash
echo "=== Rebuilding University Admission Monitor ==="

# 1. Create directory structure
echo "1. Creating directory structure..."
mkdir -p config core models scrapers notifiers filters data logs

# 2. Check what files we have
echo -e "\n2. Inventory of existing files..."
EXISTING_FILES=$(find . -maxdepth 2 -type f -name "*.py" -o -name "*.yaml" -o -name "*.yml" -o -name "*.json" -o -name "*.md" | grep -v rebuild_project.sh | sort)
if [ -n "$EXISTING_FILES" ]; then
    echo "Found files:"
    echo "$EXISTING_FILES"
else
    echo "No existing project files found"
fi

# 3. Create minimal config files
echo -e "\n3. Creating configuration files..."
if [ ! -f "config/config.yaml" ]; then
    cat > config/config.yaml << 'CONFIG'
telegram:
  bot_token: "YOUR_BOT_TOKEN_HERE"
  chat_id: "YOUR_CHAT_ID_HERE"
database:
  path: "data/state.db"
logging:
  level: "INFO"
  file: "logs/monitor.log"
CONFIG
    echo "✓ Created config/config.yaml"
else
    echo "✓ config/config.yaml already exists"
fi

if [ ! -f "config/sources.yaml" ]; then
    cat > config/sources.yaml << 'SOURCES'
sources:
  adiga:
    name: "Adiga University Portal"
    url: "https://adiga.kr"
    enabled: true
    selectors:
      article_links: ['a[href*="ArticleDetail"]', 'a[onclick*="fnDetailPopup"]']
      title: ['.title', 'h1', 'h2', 'h3']
      content: ['.content', '.article-body', '#articleContent']
SOURCES
    echo "✓ Created config/sources.yaml"
fi

if [ ! -f "config/filters.yaml" ]; then
    cat > config/filters.yaml << 'FILTERS'
departments:
  music:
    keywords: ['음악', '실용음악', '성악', '작곡', '피아노']
    priority: 1
  korean:
    keywords: ['한국어', '국어국문', '국문학']
    priority: 2
  english:
    keywords: ['영어', '영어영문', '영문학']
    priority: 3

filtering:
  min_title_length: 5
  required_keywords: ['입학', '모집', '공고']
  exclude_keywords: ['졸업', '행사', '공지']
FILTERS
    echo "✓ Created config/filters.yaml"
fi

# 4. Create core modules
echo -e "\n4. Creating core modules..."

# models/article.py
cat > models/article.py << 'ARTICLE'
from dataclasses import dataclass
from datetime import datetime
from typing import Optional

@dataclass
class Article:
    title: str
    url: str
    content: str
    source: str
    published_date: Optional[str] = None
    department: Optional[str] = None
    
    def __post_init__(self):
        if not self.published_date:
            self.published_date = datetime.now().isoformat()
    
    def get_hash(self) -> str:
        """Generate unique hash for duplicate detection"""
        import hashlib
        content = f"{self.title}:{self.url}"
        return hashlib.md5(content.encode()).hexdigest()
ARTICLE
echo "✓ Created models/article.py"

# core/base_scraper.py
cat > core/base_scraper.py << 'BASE'
import logging
import time
from abc import ABC, abstractmethod
from typing import List, Dict, Any
import requests
from urllib.parse import urljoin
from models.article import Article

class BaseScraper(ABC):
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.base_url = config.get('url', '')
        self.logger = logging.getLogger(self.__class__.__name__)
        self.session = self._create_session()
    
    def _create_session(self) -> requests.Session:
        """Create requests session with proper headers"""
        session = requests.Session()
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7',
        }
        session.headers.update(headers)
        return session
    
    def resolve_link(self, href: str, onclick: str = '') -> str:
        """Resolve JavaScript links like fnDetailPopup('12345')"""
        import re
        
        # Check for JavaScript links
        js_patterns = [
            r"fnDetailPopup\s*\(\s*['\"]?(\d+)['\"]?\s*\)",
            r"location\.href\s*=\s*['\"]([^'\"]+)['\"]",
            r"open\s*\(\s*['\"]([^'\"]+)['\"]"
        ]
        
        for pattern in js_patterns:
            match = re.search(pattern, onclick)
            if match:
                article_id = match.group(1)
                if 'fnDetailPopup' in onclick:
                    return f"{self.base_url}/ArticleDetail.do?articleID={article_id}"
                return urljoin(self.base_url, article_id)
        
        # Handle regular links
        if href and href.startswith('javascript:'):
            return self.base_url
        
        if href and not href.startswith(('http://', 'https://')):
            return urljoin(self.base_url, href)
        
        return href if href else self.base_url
    
    @abstractmethod
    def fetch_articles(self) -> List[Dict[str, Any]]:
        """Fetch raw article data from source"""
        pass
    
    @abstractmethod
    def parse_article(self, raw_data: Dict[str, Any]) -> Article:
        """Parse raw data into Article object"""
        pass
    
    @abstractmethod
    def get_source_name(self) -> str:
        """Return unique source identifier"""
        pass
    
    def scrape(self) -> List[Article]:
        """Main scraping method"""
        try:
            raw_articles = self.fetch_articles()
            articles = []
            
            for raw in raw_articles:
                try:
                    article = self.parse_article(raw)
                    if article and article.title and article.url:
                        articles.append(article)
                        self.logger.debug(f"Parsed: {article.title}")
                except Exception as e:
                    self.logger.error(f"Error parsing article: {e}")
            
            self.logger.info(f"Scraped {len(articles)} articles from {self.get_source_name()}")
            return articles
            
        except Exception as e:
            self.logger.error(f"Scraping failed: {e}")
            return []
BASE
echo "✓ Created core/base_scraper.py"

# scrapers/adiga_scraper.py
cat > scrapers/adiga_scraper.py << 'ADIGA'
import time
from typing import List, Dict, Any
from bs4 import BeautifulSoup
from core.base_scraper import BaseScraper
from models.article import Article

class AdigaScraper(BaseScraper):
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.source_name = "adiga"
    
    def get_source_name(self) -> str:
        return self.source_name
    
    def fetch_articles(self) -> List[Dict[str, Any]]:
        """Fetch articles from Adiga main page"""
        try:
            response = self.session.get(self.base_url, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            articles = []
            
            # Look for article links - multiple selector patterns
            selectors = [
                'a[href*="ArticleDetail"]',
                'a[onclick*="fnDetailPopup"]',
                '.article-list a',
                '.news-item a',
                'table a',
                'tr td a'
            ]
            
            all_links = []
            for selector in selectors:
                links = soup.select(selector)
                if links:
                    all_links.extend(links[:15])  # Limit for testing
            
            # Deduplicate links
            seen_urls = set()
            for link in all_links:
                try:
                    href = link.get('href', '')
                    onclick = link.get('onclick', '')
                    title = link.get_text(strip=True)
                    
                    if not title or len(title) < 5:
                        continue
                    
                    # Resolve URL
                    url = self.resolve_link(href, onclick)
                    
                    if url in seen_urls:
                        continue
                    
                    seen_urls.add(url)
                    
                    articles.append({
                        'title': title,
                        'url': url,
                        'raw_element': str(link),
                        'onclick': onclick,
                        'href': href
                    })
                    
                except Exception as e:
                    self.logger.debug(f"Skipping link: {e}")
            
            return articles[:10]  # Return first 10 for testing
            
        except Exception as e:
            self.logger.error(f"Failed to fetch articles: {e}")
            return []
    
    def parse_article(self, raw_data: Dict[str, Any]) -> Article:
        """Parse article data"""
        try:
            # Try to fetch article content
            content = ""
            try:
                article_resp = self.session.get(raw_data['url'], timeout=5)
                if article_resp.status_code == 200:
                    article_soup = BeautifulSoup(article_resp.content, 'html.parser')
                    
                    # Try multiple content selectors
                    content_selectors = [
                        '.article-content',
                        '.content',
                        '.board-view',
                        'div[class*="content"]',
                        'div[class*="article"]',
                        'td[class*="content"]'
                    ]
                    
                    for selector in content_selectors:
                        element = article_soup.select_one(selector)
                        if element:
                            content = element.get_text(strip=True, separator=' ')
                            if len(content) > 50:
                                break
                    
                    if not content or len(content) < 50:
                        # Fallback: get body text
                        body = article_soup.find('body')
                        if body:
                            content = body.get_text(strip=True, separator=' ')[:500]
            except:
                content = "Content not available"
            
            return Article(
                title=raw_data['title'],
                url=raw_data['url'],
                content=content,
                source=self.source_name
            )
            
        except Exception as e:
            self.logger.error(f"Failed to parse article: {e}")
            return Article(
                title=raw_data.get('title', 'Unknown'),
                url=raw_data.get('url', self.base_url),
                content="",
                source=self.source_name
            )
ADIGA
echo "✓ Created scrapers/adiga_scraper.py"

# notifiers/telegram_notifier.py
cat > notifiers/telegram_notifier.py << 'TELEGRAM'
import logging
import requests
from typing import Optional

class TelegramNotifier:
    def __init__(self, config: dict):
        self.bot_token = config.get('bot_token', '')
        self.chat_id = config.get('chat_id', '')
        self.logger = logging.getLogger(__name__)
    
    def send_message(self, message: str, parse_mode: str = "HTML") -> bool:
        """Send message to Telegram"""
        if not self.bot_token or not self.chat_id:
            self.logger.error("Telegram credentials not configured")
            return False
        
        try:
            url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"
            payload = {
                'chat_id': self.chat_id,
                'text': message,
                'parse_mode': parse_mode,
                'disable_web_page_preview': False
            }
            
            response = requests.post(url, json=payload, timeout=10)
            
            if response.status_code == 200:
                self.logger.debug(f"Message sent successfully")
                return True
            else:
                self.logger.error(f"Failed to send message: {response.status_code} - {response.text}")
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
TELEGRAM
echo "✓ Created notifiers/telegram_notifier.py"

# core/monitor_engine.py (simplified working version)
cat > core/monitor_engine.py << 'MONITOR'
#!/usr/bin/env python3
"""
University Admission Monitor - Main Engine
"""
import yaml
import logging
import sqlite3
import hashlib
from datetime import datetime, timedelta
from typing import List, Dict, Any
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.article import Article
from scrapers.adiga_scraper import AdigaScraper
from notifiers.telegram_notifier import TelegramNotifier

class MonitorEngine:
    def __init__(self, config_path: str = "config/config.yaml"):
        self.config = self.load_config(config_path)
        self.setup_logging()
        self.telegram = TelegramNotifier(self.config['telegram'])
        self.db_path = self.config['database']['path']
        self.setup_database()
        
    def load_config(self, config_path: str) -> dict:
        """Load configuration from YAML"""
        with open(config_path, 'r') as f:
            return yaml.safe_load(f)
    
    def setup_logging(self):
        """Setup logging configuration"""
        log_config = self.config['logging']
        logging.basicConfig(
            level=log_config['level'],
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_config['file']),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def setup_database(self):
        """Setup SQLite database for state tracking"""
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create tables
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS articles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            hash TEXT UNIQUE NOT NULL,
            title TEXT NOT NULL,
            url TEXT NOT NULL,
            source TEXT NOT NULL,
            department TEXT,
            sent_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        
        # Create index for faster lookups
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_hash ON articles (hash)')
        
        conn.commit()
        conn.close()
    
    def is_duplicate(self, article_hash: str) -> bool:
        """Check if article has already been sent"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT 1 FROM articles WHERE hash = ?', (article_hash,))
        result = cursor.fetchone()
        
        conn.close()
        return result is not None
    
    def mark_as_sent(self, article: Article):
        """Mark article as sent in database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
            INSERT OR IGNORE INTO articles (hash, title, url, source, department)
            VALUES (?, ?, ?, ?, ?)
            ''', (article.get_hash(), article.title, article.url, article.source, article.department))
            
            conn.commit()
            self.logger.debug(f"Marked as sent: {article.title}")
        except Exception as e:
            self.logger.error(f"Error marking article: {e}")
        finally:
            conn.close()
    
    def load_filters(self) -> Dict[str, List[str]]:
        """Load department filters"""
        with open('config/filters.yaml', 'r') as f:
            filters = yaml.safe_load(f)
        
        department_filters = {}
        for dept, config in filters.get('departments', {}).items():
            department_filters[dept] = config.get('keywords', [])
        
        return department_filters
    
    def filter_article(self, article: Article, filters: Dict[str, List[str]]) -> str:
        """Determine which department an article belongs to"""
        text_to_check = f"{article.title} {article.content}".lower()
        
        for department, keywords in filters.items():
            for keyword in keywords:
                if keyword.lower() in text_to_check:
                    return department
        
        return "general"
    
    def format_message(self, article: Article, department: str) -> str:
        """Format article as Telegram message"""
        # Truncate content if too long
        content = article.content
        if len(content) > 300:
            content = content[:297] + "..."
        
        message = f"""
🎓 <b>새 입학 공고</b>

<b>제목:</b> {article.title}

<b>부서:</b> {department}
<b>내용:</b> {content}

<b>링크:</b> {article.url}

<b>출처:</b> {article.source}
#{department} #{article.source}
"""
        return message.strip()
    
    def test_scraping(self) -> List[Article]:
        """Test scraping without sending notifications"""
        self.logger.info("=== TEST MODE: Scraping without notifications ===")
        
        # Load source configuration
        with open('config/sources.yaml', 'r') as f:
            sources_config = yaml.safe_load(f)
        
        articles = []
        
        # Initialize and test Adiga scraper
        if 'adiga' in sources_config.get('sources', {}):
            adiga_config = sources_config['sources']['adiga']
            scraper = AdigaScraper(adiga_config)
            
            self.logger.info(f"Testing scraper: {scraper.get_source_name()}")
            scraped = scraper.scrape()
            articles.extend(scraped)
            
            for article in scraped:
                self.logger.info(f"  Found: {article.title}")
                self.logger.info(f"    URL: {article.url}")
                if article.content:
                    self.logger.info(f"    Content preview: {article.content[:100]}...")
        
        return articles
    
    def run(self, test_mode: bool = False):
        """Run the monitoring cycle"""
        self.logger.info("Starting University Admission Monitor")
        
        # Test Telegram connection
        if not self.telegram.test_connection():
            self.logger.error("Telegram connection failed. Check bot token.")
            return
        
        self.logger.info("Telegram connection successful")
        
        # Load configurations
        with open('config/sources.yaml', 'r') as f:
            sources_config = yaml.safe_load(f)
        
        department_filters = self.load_filters()
        
        # Initialize scrapers
        scrapers = []
        if 'adiga' in sources_config.get('sources', {}):
            adiga_config = sources_config['sources']['adiga']
            if adiga_config.get('enabled', True):
                scrapers.append(AdigaScraper(adiga_config))
        
        if not scrapers:
            self.logger.error("No scrapers configured or enabled")
            return
        
        # Scrape articles
        all_articles = []
        for scraper in scrapers:
            self.logger.info(f"Scraping from {scraper.get_source_name()}")
            articles = scraper.scrape()
            all_articles.extend(articles)
            self.logger.info(f"Found {len(articles)} articles from {scraper.get_source_name()}")
        
        # Filter and process articles
        new_articles = []
        for article in all_articles:
            # Apply department filter
            department = self.filter_article(article, department_filters)
            article.department = department
            
            # Check for duplicates
            if not self.is_duplicate(article.get_hash()):
                new_articles.append(article)
                self.mark_as_sent(article)
        
        # Send notifications (unless in test mode)
        if test_mode:
            self.logger.info(f"TEST MODE: Would send {len(new_articles)} notifications")
            for article in new_articles:
                message = self.format_message(article, article.department)
                self.logger.info(f"Would send:\n{message}\n")
        else:
            if new_articles:
                self.logger.info(f"Sending {len(new_articles)} notifications")
                for article in new_articles:
                    message = self.format_message(article, article.department)
                    if self.telegram.send_message(message):
                        self.logger.info(f"Notification sent: {article.title}")
                    else:
                        self.logger.error(f"Failed to send: {article.title}")
                    
                    # Small delay to avoid rate limiting
                    import time
                    time.sleep(1)
            else:
                self.logger.info("No new articles to notify")
        
        self.logger.info("Monitoring cycle completed")

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='University Admission Monitor')
    parser.add_argument('--test', action='store_true', help='Test mode (no notifications)')
    parser.add_argument('--scrape-test', action='store_true', help='Test scraping only')
    
    args = parser.parse_args()
    
    monitor = MonitorEngine()
    
    if args.scrape_test:
        articles = monitor.test_scraping()
        print(f"\nTotal articles found: {len(articles)}")
    else:
        monitor.run(test_mode=args.test)

if __name__ == "__main__":
    main()
MONITOR
echo "✓ Created core/monitor_engine.py"

# 5. Create requirements.txt
cat > requirements.txt << 'REQUIREMENTS'
requests>=2.28.0
beautifulsoup4>=4.11.0
PyYAML>=6.0
REQUIREMENTS
echo "✓ Created requirements.txt"

# 6. Make scripts executable
chmod +x core/monitor_engine.py

# 7. Create test script
cat > test_rebuild.sh << 'TEST'
#!/bin/bash
echo "=== Testing Rebuilt System ==="
echo "1. Testing Python imports..."
python3 -c "
import sys
sys.path.insert(0, '.')
try:
    from models.article import Article
    from scrapers.adiga_scraper import AdigaScraper
    from notifiers.telegram_notifier import TelegramNotifier
    print('✓ All imports successful')
    
    # Test Article model
    article = Article('Test', 'https://example.com', 'Content', 'test')
    print(f'✓ Article model works: {article.get_hash()}')
    
except ImportError as e:
    print(f'✗ Import error: {e}')
    import traceback
    traceback.print_exc()
"

echo -e "\n2. Testing configuration..."
if [ -f "config/config.yaml" ]; then
    echo "✓ config/config.yaml exists"
    python3 -c "
import yaml
with open('config/config.yaml', 'r') as f:
    config = yaml.safe_load(f)
    print('  Telegram configured:', 'bot_token' in config.get('telegram', {}))
    print('  Database path:', config.get('database', {}).get('path', 'Not set'))
"
else
    echo "✗ config/config.yaml missing"
fi

echo -e "\n3. Testing Adiga scraper..."
python3 -c "
import sys
sys.path.insert(0, '.')
try:
    from scrapers.adiga_scraper import AdigaScraper
    
    config = {
        'url': 'https://adiga.kr',
        'name': 'Test Adiga'
    }
    
    scraper = AdigaScraper(config)
    print(f'✓ AdigaScraper initialized: {scraper.get_source_name()}')
    
    # Test link resolution
    test_onclick = \"fnDetailPopup('12345')\"
    resolved = scraper.resolve_link('', test_onclick)
    print(f'✓ JavaScript link resolution: {test_onclick} -> {resolved}')
    
except Exception as e:
    print(f'✗ Error: {e}')
"

echo -e "\n4. Directory structure:"
find . -type d -maxdepth 2 | sort

echo -e "\n=== Rebuild Complete ==="
echo -e "\nNext steps:"
echo "1. Edit config/config.yaml with your Telegram bot credentials"
echo "2. Test scraping: python core/monitor_engine.py --scrape-test"
echo "3. Test with notifications: python core/monitor_engine.py --test"
echo "4. Run for real: python core/monitor_engine.py"
TEST
chmod +x test_rebuild.sh

echo -e "\n=== Rebuild Complete ==="
echo -e "\nRun the test to verify:"
echo "  ./test_rebuild.sh"
echo -e "\nThen configure your Telegram credentials in config/config.yaml"
