#!/bin/bash
echo "=== Fixing JavaScript Rendering Issue ==="

# Install selenium for JavaScript rendering
pip install selenium webdriver-manager

# Create a JavaScript-aware scraper
cat > scrapers/adiga_js_scraper.py << 'PYSCRIPT'
"""
Adiga scraper using Selenium for JavaScript rendering
"""
import time
from typing import List, Dict, Any
import re
from core.base_scraper import BaseScraper
from models.article import Article

class AdigaJsScraper(BaseScraper):
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.source_name = "adiga"
        self.driver = None
    
    def get_source_name(self) -> str:
        return self.source_name
    
    def _init_driver(self):
        """Initialize Selenium WebDriver"""
        try:
            from selenium import webdriver
            from selenium.webdriver.chrome.options import Options
            from selenium.webdriver.common.by import By
            from selenium.webdriver.support.ui import WebDriverWait
            from selenium.webdriver.support import expected_conditions as EC
            from webdriver_manager.chrome import ChromeDriverManager
            from selenium.webdriver.chrome.service import Service
            
            chrome_options = Options()
            chrome_options.add_argument('--headless')  # Run in background
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            chrome_options.add_argument('--disable-gpu')
            chrome_options.add_argument('--window-size=1920,1080')
            chrome_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
            
            # Initialize driver
            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            self.driver.set_page_load_timeout(30)
            
            return True
        except Exception as e:
            self.logger.error(f"Failed to initialize WebDriver: {e}")
            return False
    
    def fetch_articles(self) -> List[Dict[str, Any]]:
        """Fetch articles using Selenium to handle JavaScript"""
        try:
            # Initialize driver if not already done
            if not self.driver and not self._init_driver():
                return []
            
            print(f"DEBUG: Fetching {self.base_url} with Selenium...")
            
            # Load the page
            self.driver.get(self.base_url)
            
            # Wait for page to load
            time.sleep(3)
            
            # Take screenshot for debugging
            self.driver.save_screenshot('adiga_selenium_screenshot.png')
            print("DEBUG: Saved screenshot to adiga_selenium_screenshot.png")
            
            # Save page source
            page_source = self.driver.page_source
            with open('adiga_selenium_source.html', 'w', encoding='utf-8') as f:
                f.write(page_source)
            print(f"DEBUG: Saved page source ({len(page_source)} bytes)")
            
            # Parse with BeautifulSoup
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(page_source, 'html.parser')
            
            articles = []
            
            # Strategy 1: Look for onclick with fnDetailPopup
            print("DEBUG: Looking for fnDetailPopup in onclick attributes...")
            onclick_elements = soup.find_all(attrs={'onclick': re.compile(r'fnDetailPopup', re.I)})
            print(f"DEBUG: Found {len(onclick_elements)} elements with fnDetailPopup")
            
            for element in onclick_elements[:20]:
                try:
                    onclick = element.get('onclick', '')
                    if not onclick:
                        continue
                    
                    # Extract article ID
                    match = re.search(r"fnDetailPopup\s*\(\s*['\"]?(\d+)['\"]?\s*\)", onclick)
                    if not match:
                        continue
                    
                    article_id = match.group(1)
                    
                    # Get text
                    text = element.get_text(strip=True)
                    if not text or len(text) < 5:
                        # Look for text in nearby elements
                        parent = element.parent
                        if parent:
                            text = parent.get_text(strip=True)
                    
                    if not text or len(text) < 5:
                        continue
                    
                    # Construct URL
                    url = f"{self.base_url}/ArticleDetail.do?articleID={article_id}"
                    
                    articles.append({
                        'title': text[:200],
                        'url': url,
                        'onclick': onclick,
                        'article_id': article_id,
                        'element_html': str(element)[:500]
                    })
                    
                    print(f"DEBUG: Found via onclick: {text[:50]}... -> {url}")
                    
                except Exception as e:
                    print(f"DEBUG: Error processing onclick element: {e}")
                    continue
            
            # Strategy 2: Look for links in the page
            if len(articles) < 3:
                print("DEBUG: Looking for all links...")
                all_links = soup.find_all('a')
                print(f"DEBUG: Found {len(all_links)} total links")
                
                for link in all_links[:50]:
                    try:
                        href = link.get('href', '')
                        text = link.get_text(strip=True)
                        
                        if not text or len(text) < 10:
                            continue
                        
                        # Skip common non-article links
                        if any(skip in text.lower() for skip in ['로그인', '회원가입', '검색', '이전', '다음']):
                            continue
                        
                        # Construct URL
                        if href and not href.startswith(('http://', 'https://', 'javascript:', '#')):
                            if href.startswith('/'):
                                url = f"{self.base_url}{href}"
                            else:
                                url = f"{self.base_url}/{href}"
                        elif href.startswith('javascript:'):
                            onclick = link.get('onclick', '')
                            if 'fnDetailPopup' in onclick:
                                match = re.search(r"fnDetailPopup\s*\(\s*['\"]?(\d+)['\"]?\s*\)", onclick)
                                if match:
                                    article_id = match.group(1)
                                    url = f"{self.base_url}/ArticleDetail.do?articleID={article_id}"
                                else:
                                    continue
                            else:
                                continue
                        else:
                            url = href if href else self.base_url
                        
                        # Check if we already have this URL
                        if any(a['url'] == url for a in articles):
                            continue
                        
                        articles.append({
                            'title': text[:200],
                            'url': url,
                            'href': href,
                            'onclick': link.get('onclick', '')
                        })
                        
                        print(f"DEBUG: Found via link: {text[:50]}... -> {url}")
                        
                    except Exception as e:
                        print(f"DEBUG: Error processing link: {e}")
                        continue
            
            # Strategy 3: Look for text containing university-related terms
            if len(articles) < 5:
                print("DEBUG: Searching for university-related text...")
                
                keywords = [
                    '입학', '모집', '공고', '안내', '전형', '대학',
                    '학과', '학부', '원서접수', '모집요강', '정시',
                    '수시', '추가모집', '정원', '합격', '발표'
                ]
                
                for keyword in keywords:
                    elements = soup.find_all(string=re.compile(keyword, re.I))
                    for element in elements[:10]:
                        try:
                            parent = element.parent
                            if parent and parent.name == 'a':
                                href = parent.get('href', '')
                                onclick = parent.get('onclick', '')
                                text = parent.get_text(strip=True)
                                
                                if text and len(text) >= 10:
                                    # Construct URL
                                    if href and not href.startswith(('http://', 'https://', 'javascript:', '#')):
                                        if href.startswith('/'):
                                            url = f"{self.base_url}{href}"
                                        else:
                                            url = f"{self.base_url}/{href}"
                                    elif href.startswith('javascript:') and 'fnDetailPopup' in onclick:
                                        match = re.search(r"fnDetailPopup\s*\(\s*['\"]?(\d+)['\"]?\s*\)", onclick)
                                        if match:
                                            article_id = match.group(1)
                                            url = f"{self.base_url}/ArticleDetail.do?articleID={article_id}"
                                        else:
                                            continue
                                    else:
                                        continue
                                    
                                    # Check if already added
                                    if any(a['url'] == url for a in articles):
                                        continue
                                    
                                    articles.append({
                                        'title': text[:200],
                                        'url': url,
                                        'href': href,
                                        'onclick': onclick
                                    })
                                    
                                    print(f"DEBUG: Found via keyword '{keyword}': {text[:50]}...")
                        except:
                            continue
            
            print(f"DEBUG: Total articles found: {len(articles)}")
            return articles
            
        except Exception as e:
            print(f"DEBUG: Selenium fetch error: {e}")
            import traceback
            traceback.print_exc()
            return []
    
    def parse_article(self, raw_data: Dict[str, Any]) -> Article:
        """Parse article using Selenium for JavaScript content"""
        try:
            print(f"DEBUG: Parsing article: {raw_data['title'][:50]}...")
            
            content = ""
            
            try:
                if raw_data['url'] and raw_data['url'] != self.base_url:
                    print(f"DEBUG: Fetching article page: {raw_data['url']}")
                    
                    # Use Selenium to load article page
                    self.driver.get(raw_data['url'])
                    time.sleep(2)
                    
                    # Save article page
                    article_source = self.driver.page_source
                    with open('adiga_article_source.html', 'w', encoding='utf-8') as f:
                        f.write(article_source)
                    
                    # Parse with BeautifulSoup
                    from bs4 import BeautifulSoup
                    article_soup = BeautifulSoup(article_source, 'html.parser')
                    
                    # Try to find content
                    content_selectors = [
                        '.article-content',
                        '.content',
                        '.board-view',
                        '.view-content',
                        '#articleContent',
                        '#content',
                        'div[class*="content"]',
                        'div[class*="article"]',
                        'td[class*="content"]',
                        '.bd',
                        '.body',
                        'article',
                        'main'
                    ]
                    
                    for selector in content_selectors:
                        element = article_soup.select_one(selector)
                        if element:
                            content = element.get_text(strip=True, separator=' ')
                            print(f"DEBUG: Found content with selector '{selector}', length: {len(content)}")
                            if len(content) > 100:
                                break
                    
                    if not content or len(content) < 100:
                        # Fallback: get body text
                        for tag in article_soup(['script', 'style', 'nav', 'header', 'footer']):
                            tag.decompose()
                        
                        body = article_soup.find('body')
                        if body:
                            content = body.get_text(strip=True, separator=' ')[:1500]
                            print(f"DEBUG: Using body text, length: {len(content)}")
                
            except Exception as e:
                print(f"DEBUG: Error fetching article content: {e}")
                content = f"Error: {str(e)[:100]}"
            
            # Create article
            article = Article(
                title=raw_data['title'],
                url=raw_data['url'],
                content=content,
                source=self.source_name
            )
            
            return article
            
        except Exception as e:
            print(f"DEBUG: Parse error: {e}")
            return Article(
                title=raw_data.get('title', 'Unknown'),
                url=raw_data.get('url', self.base_url),
                content=f"Parse error: {str(e)[:100]}",
                source=self.source_name
            )
    
    def __del__(self):
        """Clean up driver"""
        if self.driver:
            self.driver.quit()
PYSCRIPT

echo "✓ Created JavaScript-aware scraper"

# Update the monitor engine to use the new scraper
cat > core/monitor_engine_js.py << 'PYSCRIPT'
#!/usr/bin/env python3
"""
Monitor engine with JavaScript support
"""
import yaml
import logging
import sqlite3
import hashlib
from datetime import datetime
from typing import List, Dict, Any
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.article import Article
from scrapers.adiga_js_scraper import AdigaJsScraper
from notifiers.telegram_notifier import TelegramNotifier

class JsMonitorEngine:
    def __init__(self, config_path: str = "config/config.yaml"):
        self.config = self.load_config(config_path)
        self.setup_logging()
        self.telegram = TelegramNotifier(self.config['telegram'])
        self.db_path = self.config['database']['path']
        self.setup_database()
        
    def load_config(self, config_path: str) -> dict:
        with open(config_path, 'r') as f:
            return yaml.safe_load(f)
    
    def setup_logging(self):
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
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
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
        
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_hash ON articles (hash)')
        conn.commit()
        conn.close()
    
    def is_duplicate(self, article_hash: str) -> bool:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT 1 FROM articles WHERE hash = ?', (article_hash,))
        result = cursor.fetchone()
        conn.close()
        return result is not None
    
    def mark_as_sent(self, article: Article):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        try:
            cursor.execute('''
            INSERT OR IGNORE INTO articles (hash, title, url, source, department)
            VALUES (?, ?, ?, ?, ?)
            ''', (article.get_hash(), article.title, article.url, article.source, article.department))
            conn.commit()
        except Exception as e:
            self.logger.error(f"Error marking article: {e}")
        finally:
            conn.close()
    
    def load_filters(self) -> Dict[str, List[str]]:
        with open('config/filters.yaml', 'r') as f:
            filters = yaml.safe_load(f)
        
        department_filters = {}
        for dept, config in filters.get('departments', {}).items():
            department_filters[dept] = config.get('keywords', [])
        
        return department_filters
    
    def filter_article(self, article: Article, filters: Dict[str, List[str]]) -> str:
        text_to_check = f"{article.title} {article.content}".lower()
        
        for department, keywords in filters.items():
            for keyword in keywords:
                if keyword.lower() in text_to_check:
                    return department
        
        return "general"
    
    def format_message(self, article: Article, department: str) -> str:
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
    
    def run(self, test_mode: bool = False):
        self.logger.info("Starting JavaScript-aware Monitor")
        
        # Test Telegram
        if not self.telegram.test_connection():
            self.logger.error("Telegram connection failed")
            return
        
        self.logger.info("Telegram connection successful")
        
        # Load configs
        with open('config/sources.yaml', 'r') as f:
            sources_config = yaml.safe_load(f)
        
        department_filters = self.load_filters()
        
        # Initialize scraper
        scrapers = []
        if 'adiga' in sources_config.get('sources', {}):
            adiga_config = sources_config['sources']['adiga']
            if adiga_config.get('enabled', True):
                self.logger.info("Initializing Adiga JavaScript scraper...")
                scrapers.append(AdigaJsScraper(adiga_config))
        
        if not scrapers:
            self.logger.error("No scrapers configured")
            return
        
        # Scrape
        all_articles = []
        for scraper in scrapers:
            self.logger.info(f"Scraping from {scraper.get_source_name()}")
            articles = scraper.scrape()
            all_articles.extend(articles)
            self.logger.info(f"Found {len(articles)} articles from {scraper.get_source_name()}")
        
        # Filter and process
        new_articles = []
        for article in all_articles:
            department = self.filter_article(article, department_filters)
            article.department = department
            
            if not self.is_duplicate(article.get_hash()):
                new_articles.append(article)
                self.mark_as_sent(article)
        
        # Send notifications
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
                    
                    import time
                    time.sleep(1)
            else:
                self.logger.info("No new articles to notify")
        
        self.logger.info("Monitoring completed")

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='JavaScript-aware Monitor')
    parser.add_argument('--test', action='store_true', help='Test mode (no notifications)')
    
    args = parser.parse_args()
    
    monitor = JsMonitorEngine()
    monitor.run(test_mode=args.test)

if __name__ == "__main__":
    main()
PYSCRIPT

echo "✓ Created JavaScript-aware monitor engine"

# Create test script
cat > test_js_scraper.sh << 'TEST'
#!/bin/bash
echo "=== Testing JavaScript Scraper ==="

# First test the scraper directly
python3 -c "
import sys
sys.path.insert(0, '.')
print('Testing AdigaJsScraper import...')
try:
    from scrapers.adiga_js_scraper import AdigaJsScraper
    print('✓ Import successful')
    
    config = {
        'url': 'https://adiga.kr',
        'name': 'Adiga JS'
    }
    
    scraper = AdigaJsScraper(config)
    print(f'✓ Scraper initialized')
    
    print('\\nFetching articles...')
    articles = scraper.fetch_articles()
    print(f'Found {len(articles)} articles')
    
    if articles:
        print('\\nFirst 3 articles:')
        for i, article in enumerate(articles[:3]):
            print(f'{i+1}. {article[\"title\"][:60]}...')
            print(f'   URL: {article[\"url\"]}')
        
        print('\\nParsing first article...')
        if articles:
            parsed = scraper.parse_article(articles[0])
            print(f'Title: {parsed.title}')
            print(f'URL: {parsed.url}')
            print(f'Content length: {len(parsed.content)} chars')
            if parsed.content:
                print(f'Preview: {parsed.content[:100]}...')
    else:
        print('\\nNo articles found. Possible issues:')
        print('1. Website structure changed')
        print('2. JavaScript blocking detected')
        print('3. Need different selectors')
        print('\\nCheck generated files:')
        print('- adiga_selenium_screenshot.png')
        print('- adiga_selenium_source.html')
    
except Exception as e:
    print(f'✗ Error: {e}')
    import traceback
    traceback.print_exc()
"

# Test with monitor engine
echo -e "\n=== Testing with Monitor Engine ==="
python3 core/monitor_engine_js.py --test

echo -e "\n=== Files Generated ==="
ls -la | grep -E "(adiga|debug|screenshot|html)"
TEST

chmod +x test_js_scraper.sh
./test_js_scraper.sh
