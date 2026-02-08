"""
Adiga scraper with Selenium - clicks popup links to extract content
"""
import time
import re
from typing import List, Dict, Any
from bs4 import BeautifulSoup

# Try importing from core, fallback if not available
try:
    from core.base_scraper import BaseScraper
    from models.article import Article
except ImportError:
    # Fallback for standalone testing
    class BaseScraper:
        def __init__(self, config):
            self.config = config
            self.base_url = config.get('url', 'https://www.adiga.kr')
            import requests
            self.session = requests.Session()
    
    class Article:
        def __init__(self, **kwargs):
            self.__dict__.update(kwargs)
            self.title = kwargs.get('title', '')
            self.url = kwargs.get('url', '')
            self.content = kwargs.get('content', '')
            self.source = kwargs.get('source', '')

class AdigaScraper(BaseScraper):
    def __init__(self, config: Dict[str, Any]):
        if 'url' not in config:
            config['url'] = "https://www.adiga.kr"
        
        super().__init__(config)
        self.source_name = "adiga"
        self.driver = None
        
    def get_source_name(self) -> str:
        return self.source_name
    
    def _init_selenium(self):
        """Initialize Selenium WebDriver with Chrome Beta"""
        try:
            from selenium import webdriver
            from selenium.webdriver.chrome.options import Options
            from selenium.webdriver.chrome.service import Service
            
            print("DEBUG: Initializing Selenium with Chrome Beta 145...")
            
            options = Options()
            options.add_argument('--headless=new')
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('--disable-gpu')
            options.add_argument('--window-size=1920,1080')
            options.add_argument('--user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36')
            
            # Use Chrome Beta
            options.binary_location = '/usr/bin/google-chrome-beta'
            
            # Use ChromeDriver (beta version at /usr/bin/chromedriver)
            service = Service('/usr/bin/chromedriver')
            self.driver = webdriver.Chrome(service=service, options=options)
            self.driver.set_page_load_timeout(30)
            
            print("DEBUG: Selenium initialized successfully")
            return True
            
        except Exception as e:
            print(f"DEBUG: Selenium initialization failed: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def fetch_articles(self) -> List[Dict[str, Any]]:
        """Fetch articles by clicking popup links with Selenium"""
        print("=" * 80)
        print("ADIGA SCRAPER - CLICKING POPUPS FOR CONTENT")
        print("=" * 80)
        
        # Initialize Selenium
        if not self._init_selenium():
            print("ERROR: Could not initialize Selenium")
            return []
        
        articles = []
        
        try:
            from selenium.webdriver.common.by import By
            from selenium.webdriver.support.ui import WebDriverWait
            from selenium.webdriver.support import expected_conditions as EC
            
            # Navigate to the news page
            url = "https://www.adiga.kr/uct/nmg/enw/newsView.do?menuId=PCUCTNMG2000"
            print(f"📋 Fetching: {url}")
            
            self.driver.get(url)
            time.sleep(3)
            
            print(f"   Status: Page loaded")
            
            # Find all popup links
            popup_links = self.driver.find_elements(By.XPATH, "//a[contains(@onclick, 'fnDetailPopup')]")
            print(f"   ✓ Found {len(popup_links)} popup links")
            
            # Process each link (limit to first 10 for testing)
            for idx, link in enumerate(popup_links[:10]):
                try:
                    # Get article info before clicking
                    onclick = link.get_attribute('onclick')
                    match = re.search(r'fnDetailPopup\s*\(\s*["\'](\d+)["\']\s*\)', onclick)
                    if not match:
                        continue
                    
                    article_id = match.group(1)
                    
                    # Get title
                    try:
                        title_elem = link.find_element(By.CLASS_NAME, 'uctCastTitle')
                        title = title_elem.text.strip()
                    except:
                        title = link.text.strip()
                    
                    if not title or len(title) < 5:
                        continue
                    
                    print(f"\n   [{idx+1}] Clicking: {title[:60]}... (ID: {article_id})")
                    
                    # Click the link to open popup
                    self.driver.execute_script("arguments[0].click();", link)
                    time.sleep(2)  # Wait for popup to load
                    
                    # Extract content from popup
                    page_source = self.driver.page_source
                    soup = BeautifulSoup(page_source, 'html.parser')
                    
                    # Look for popup content
                    # Common popup selectors
                    content = ""
                    popup_selectors = [
                        {'class': 'popCont'},
                        {'class': 'modal-body'},
                        {'class': 'popup-content'},
                        {'id': 'newsDetail'},
                        {'class': 'detail-content'},
                    ]
                    
                    for selector in popup_selectors:
                        popup_elem = soup.find('div', selector)
                        if popup_elem:
                            # Remove scripts and styles
                            for tag in popup_elem(['script', 'style']):
                                tag.decompose()
                            content = popup_elem.get_text(strip=True, separator=' ')[:500]
                            if content:
                                break
                    
                    if not content:
                        # Fallback: get any visible text that appeared after click
                        content = title
                    
                    # Check for admission keywords
                    admission_keywords = ['입학', '모집', '공고', '전형', '원서', '입시', '수시', '정시', '학과']
                    title_lower = title.lower()
                    content_lower = content.lower()
                    combined = title_lower + ' ' + content_lower
                    
                    is_admission = any(kw in combined for kw in admission_keywords)
                    
                    if is_admission:
                        articles.append({
                            'title': title,
                            'url': f"https://www.adiga.kr/uct/nmg/enw/newsView.do?menuId=PCUCTNMG2000#article_{article_id}",
                            'article_id': article_id,
                            'content': content
                        })
                        print(f"       ✓ Extracted {len(content)} chars of content")
                    else:
                        print(f"       ✗ Not admission-related")
                    
                    # Close popup if there's a close button
                    try:
                        close_button = self.driver.find_element(By.XPATH, "//button[contains(@class, 'close') or contains(text(), '닫기')]")
                        close_button.click()
                        time.sleep(0.5)
                    except:
                        # Popup might auto-close or no close button
                        pass
                    
                except Exception as e:
                    print(f"       Error processing link: {e}")
                    continue
            
            print("\n" + "=" * 80)
            print(f"RESULT: {len(articles)} admission-related articles extracted")
            print("=" * 80)
            
            return articles
            
        except Exception as e:
            print(f"ERROR: {e}")
            import traceback
            traceback.print_exc()
            return []
        
        finally:
            if self.driver:
                self.driver.quit()
                print("DEBUG: Selenium driver closed")
    
    def parse_article(self, raw_data: Dict[str, Any]) -> Article:
        """Parse raw article data into Article object"""
        return Article(
            title=raw_data.get('title', 'No Title'),
            url=raw_data.get('url', ''),
            content=raw_data.get('content', raw_data.get('title', '')),
            source=self.source_name
        )

def test_scraper():
    """Test the scraper"""
    print("🧪 Testing AdigaScraper with Popup Clicking...\n")
    
    scraper = AdigaScraper({'url': 'https://www.adiga.kr'})
    articles = scraper.fetch_articles()
    
    print(f"\n📊 Results: {len(articles)} articles found\n")
    
    for i, article in enumerate(articles, 1):
        print(f"{i}. {article['title']}")
        print(f"   URL: {article['url']}")
        print(f"   Content: {article['content'][:100]}...")
        print()
    
    if articles:
        print("\n" + "=" * 80)
        print("SAMPLE PARSED ARTICLE:")
        print("=" * 80)
        parsed = scraper.parse_article(articles[0])
        print(f"Title: {parsed.title}")
        print(f"URL: {parsed.url}")
        print(f"Content length: {len(parsed.content)} chars")
        print(f"Content: {parsed.content[:300]}...")
    
    return articles

if __name__ == "__main__":
    test_scraper()
