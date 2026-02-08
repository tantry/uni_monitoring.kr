"""
Template for new scraper implementations

IMPORTANT: Before starting, read SCRAPER_DEVELOPMENT_GUIDE.md
Complete the Pre-Development Checklist to identify website patterns.
"""
import time
import re
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime

# Core imports - try both paths for flexibility
try:
    from core.base_scraper import BaseScraper
    from models.article import Article
except ImportError:
    # Fallback for standalone testing
    class BaseScraper:
        def __init__(self, config):
            self.config = config
            self.base_url = config.get('url', '')
            import requests
            self.session = requests.Session()
    
    class Article:
        def __init__(self, **kwargs):
            self.__dict__.update(kwargs)

logger = logging.getLogger(__name__)

class TemplateScraper(BaseScraper):
    """
    Template scraper for [SOURCE NAME]
    
    Website Pattern: [CHOOSE ONE]
    - [ ] Simple HTTP (static HTML)
    - [ ] JavaScript-rendered (needs Selenium)
    - [ ] Popup-based articles (needs Selenium + clicking)
    - [ ] Requires authentication
    
    Special Requirements:
    - [ ] Cookie consent handling
    - [ ] POST requests
    - [ ] Session management
    """
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.source_name = "template_source"  # Change this
        self.base_url = config.get('url', 'https://example.com')  # Change this
        self.driver = None  # For Selenium (if needed)
        
        # Configure session headers (for HTTP requests)
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        })
    
    def get_source_name(self) -> str:
        return self.source_name
    
    # ========== SELENIUM SETUP (if needed) ==========
    
    def _init_selenium(self) -> bool:
        """
        Initialize Selenium WebDriver
        Only needed for JavaScript-rendered sites
        """
        try:
            from selenium import webdriver
            from selenium.webdriver.chrome.options import Options
            from selenium.webdriver.chrome.service import Service
            
            print("DEBUG: Initializing Selenium...")
            
            options = Options()
            options.add_argument('--headless=new')
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('--disable-gpu')
            options.add_argument('--window-size=1920,1080')
            options.add_argument('--user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36')
            
            # Use system Chrome
            options.binary_location = '/usr/bin/google-chrome-beta'
            service = Service('/usr/bin/chromedriver')
            
            self.driver = webdriver.Chrome(service=service, options=options)
            self.driver.set_page_load_timeout(30)
            
            print("DEBUG: Selenium initialized successfully")
            return True
            
        except Exception as e:
            print(f"DEBUG: Selenium initialization failed: {e}")
            return False
    
    def _accept_cookies(self) -> bool:
        """
        Accept cookies - common requirement for Korean websites
        Call this BEFORE navigating to content pages
        """
        try:
            from selenium.webdriver.common.by import By
            from selenium.webdriver.support.ui import WebDriverWait
            from selenium.webdriver.support import expected_conditions as EC
            
            print("DEBUG: Checking for cookie consent...")
            
            # Visit homepage to trigger cookie popup
            self.driver.get(self.base_url)
            time.sleep(2)
            
            # Common Korean cookie consent button patterns
            cookie_selectors = [
                "//button[contains(text(), '동의')]",
                "//button[contains(text(), '확인')]",
                "//button[contains(text(), '모두 동의')]",
                "//a[contains(text(), '동의')]",
                "//button[@id='cookieAccept']",
            ]
            
            for selector in cookie_selectors:
                try:
                    button = WebDriverWait(self.driver, 3).until(
                        EC.element_to_be_clickable((By.XPATH, selector))
                    )
                    button.click()
                    print(f"DEBUG: Clicked cookie consent button")
                    time.sleep(1)
                    return True
                except:
                    continue
            
            print("DEBUG: No cookie consent button found (may already be accepted)")
            return True
            
        except Exception as e:
            print(f"DEBUG: Cookie acceptance error: {e}")
            return True  # Continue anyway
    
    # ========== MAIN SCRAPING METHODS ==========
    
    def fetch_articles(self) -> List[Dict[str, Any]]:
        """
        Main method to fetch articles
        
        Choose implementation based on website pattern:
        - Simple HTTP: Use self.session.get() + BeautifulSoup
        - JavaScript: Use Selenium
        - Popups: Use Selenium + click links
        """
        print("=" * 80)
        print(f"SCRAPING: {self.source_name}")
        print("=" * 80)
        
        articles = []
        
        # OPTION 1: Simple HTTP Request (uncomment if applicable)
        # return self._fetch_with_http()
        
        # OPTION 2: Selenium for JavaScript sites (uncomment if applicable)
        # return self._fetch_with_selenium()
        
        # OPTION 3: Selenium with popup clicking (like Adiga)
        # return self._fetch_with_popup_clicking()
        
        # Default: Mock data for template testing
        return self._fetch_mock_data()
    
    def _fetch_with_http(self) -> List[Dict[str, Any]]:
        """Simple HTTP request approach"""
        from bs4 import BeautifulSoup
        
        try:
            response = self.session.get(self.base_url, timeout=15)
            if response.status_code != 200:
                return []
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # TODO: Implement your parsing logic
            articles = []
            
            # Example:
            # links = soup.find_all('a', class_='article-link')
            # for link in links:
            #     articles.append({
            #         'title': link.get_text(strip=True),
            #         'url': link.get('href'),
            #     })
            
            return articles
            
        except Exception as e:
            print(f"ERROR: {e}")
            return []
    
    def _fetch_with_selenium(self) -> List[Dict[str, Any]]:
        """Selenium approach for JavaScript-rendered sites"""
        from bs4 import BeautifulSoup
        
        if not self._init_selenium():
            return []
        
        try:
            # Accept cookies if needed
            # self._accept_cookies()
            
            # Navigate to target page
            self.driver.get(self.base_url)
            time.sleep(3)  # Wait for JavaScript
            
            # Get rendered HTML
            page_source = self.driver.page_source
            soup = BeautifulSoup(page_source, 'html.parser')
            
            # TODO: Implement your parsing logic
            articles = []
            
            return articles
            
        finally:
            if self.driver:
                self.driver.quit()
    
    def _fetch_with_popup_clicking(self) -> List[Dict[str, Any]]:
        """
        Selenium approach for popup-based articles (like Adiga)
        Use when articles open in popups, not separate pages
        """
        from selenium.webdriver.common.by import By
        from bs4 import BeautifulSoup
        
        if not self._init_selenium():
            return []
        
        try:
            # Accept cookies if needed
            self._accept_cookies()
            
            # Navigate to page
            self.driver.get(self.base_url)
            time.sleep(3)
            
            # Find popup links
            # TODO: Update selector for your site
            popup_links = self.driver.find_elements(
                By.XPATH,
                "//a[contains(@onclick, 'openPopup')]"  # Change this
            )
            
            articles = []
            
            for link in popup_links[:10]:  # Limit for testing
                try:
                    # Get article info
                    title = link.text.strip()
                    onclick = link.get_attribute('onclick')
                    
                    # Extract ID from onclick
                    # TODO: Update regex for your site
                    match = re.search(r'openPopup\(["\'](\d+)["\']\)', onclick)
                    if not match:
                        continue
                    
                    article_id = match.group(1)
                    
                    # Click to open popup
                    self.driver.execute_script("arguments[0].click();", link)
                    time.sleep(2)
                    
                    # Extract popup content
                    page_source = self.driver.page_source
                    soup = BeautifulSoup(page_source, 'html.parser')
                    
                    # TODO: Update selector for popup content
                    popup = soup.find('div', class_='popup-content')
                    content = popup.get_text(strip=True) if popup else ""
                    
                    articles.append({
                        'title': title,
                        'url': f"{self.base_url}#article_{article_id}",
                        'content': content,
                        'article_id': article_id
                    })
                    
                    # Close popup
                    try:
                        close_btn = self.driver.find_element(
                            By.XPATH,
                            "//button[contains(@class, 'close')]"
                        )
                        close_btn.click()
                        time.sleep(0.5)
                    except:
                        pass
                    
                except Exception as e:
                    print(f"Error processing link: {e}")
                    continue
            
            return articles
            
        finally:
            if self.driver:
                self.driver.quit()
    
    def _fetch_mock_data(self) -> List[Dict[str, Any]]:
        """Mock data for template testing"""
        return [
            {
                'title': '[TEST] Sample Admission Announcement',
                'url': f'{self.base_url}/article/1',
                'content': 'This is mock data for testing the template scraper.',
            }
        ]
    
    def parse_article(self, raw_data: Dict[str, Any]) -> Article:
        """
        Parse raw article data into Article object
        """
        return Article(
            title=raw_data.get('title', 'No Title'),
            url=raw_data.get('url', ''),
            content=raw_data.get('content', raw_data.get('title', '')),
            source=self.source_name,
            published_date=datetime.now().strftime('%Y-%m-%d')
        )

# ========== TESTING ==========

def test_scraper():
    """Test the scraper"""
    print("🧪 Testing TemplateScraper...\n")
    
    scraper = TemplateScraper({'url': 'https://example.com'})
    articles = scraper.fetch_articles()
    
    print(f"\n📊 Results: {len(articles)} articles found\n")
    
    for i, article in enumerate(articles, 1):
        print(f"{i}. {article['title']}")
        print(f"   URL: {article['url']}")
        if article.get('content'):
            print(f"   Content: {article['content'][:100]}...")
        print()
    
    if articles:
        print("=" * 80)
        print("SAMPLE PARSED ARTICLE:")
        print("=" * 80)
        parsed = scraper.parse_article(articles[0])
        print(f"Title: {parsed.title}")
        print(f"URL: {parsed.url}")
        print(f"Content: {parsed.content[:200]}...")
    
    return articles

if __name__ == "__main__":
    test_scraper()
