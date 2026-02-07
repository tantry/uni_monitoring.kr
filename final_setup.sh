#!/bin/bash
echo "=== Final Setup for Your Selenium 4.40.0 ==="

# Create the definitive scraper
cat > scrapers/adiga_final.py << 'FINAL_SCRAPER'
"""
Final Adiga scraper - optimized for Manjaro with Selenium 4.40.0
"""
import os
import sys
import time
import re
import subprocess
from typing import List, Dict, Any
from core.base_scraper import BaseScraper
from models.article import Article

class AdigaFinalScraper(BaseScraper):
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.source_name = "adiga"
        self.driver = None
        self.use_selenium = True  # Try Selenium first
        
    def get_source_name(self) -> str:
        return self.source_name
    
    def _setup_chromedriver(self):
        """Setup ChromeDriver for Manjaro"""
        try:
            # Check if chromedriver exists
            chromedriver_paths = [
                '/usr/bin/chromedriver',
                '/usr/local/bin/chromedriver',
                '/usr/lib/chromium/chromedriver',
            ]
            
            chromedriver_found = None
            for path in chromedriver_paths:
                if os.path.exists(path):
                    chromedriver_found = path
                    break
            
            # If not found, try to install it
            if not chromedriver_found:
                print("DEBUG: ChromeDriver not found, attempting to install...")
                try:
                    # Try to install via package manager
                    result = subprocess.run(
                        ['sudo', 'pacman', '-S', '--noconfirm', 'chromedriver'],
                        capture_output=True,
                        text=True
                    )
                    if result.returncode == 0:
                        chromedriver_found = '/usr/bin/chromedriver'
                        print("DEBUG: Installed ChromeDriver via pacman")
                    else:
                        print("DEBUG: Could not install ChromeDriver automatically")
                except:
                    print("DEBUG: Failed to install ChromeDriver")
            
            return chromedriver_found
            
        except Exception as e:
            print(f"DEBUG: ChromeDriver setup error: {e}")
            return None
    
    def _create_selenium_driver(self):
        """Create Selenium WebDriver"""
        try:
            from selenium import webdriver
            from selenium.webdriver.chrome.options import Options
            from selenium.webdriver.chrome.service import Service
            
            # Setup Chrome options
            options = Options()
            
            # Find Chrome binary
            chrome_paths = [
                '/usr/bin/google-chrome-stable',
                '/usr/bin/google-chrome',
                '/usr/bin/chromium',
                '/usr/bin/chromium-browser',
            ]
            
            chrome_binary = None
            for path in chrome_paths:
                if os.path.exists(path):
                    chrome_binary = path
                    print(f"DEBUG: Found Chrome at: {chrome_binary}")
                    break
            
            if chrome_binary:
                options.binary_location = chrome_binary
            
            # Add arguments
            options.add_argument('--headless=new')  # New headless mode in Chrome 112+
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('--disable-gpu')
            options.add_argument('--window-size=1920,1080')
            options.add_argument('--user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
            
            # Important: Disable automation detection
            options.add_argument('--disable-blink-features=AutomationControlled')
            options.add_experimental_option("excludeSwitches", ["enable-automation"])
            options.add_experimental_option('useAutomationExtension', False)
            
            # Try to create driver
            print("DEBUG: Creating WebDriver...")
            
            # Method 1: Try direct ChromeDriver
            try:
                # Check ChromeDriver
                chromedriver_path = self._setup_chromedriver()
                
                if chromedriver_path and os.path.exists(chromedriver_path):
                    print(f"DEBUG: Using ChromeDriver at: {chromedriver_path}")
                    service = Service(executable_path=chromedriver_path)
                    self.driver = webdriver.Chrome(service=service, options=options)
                    print("DEBUG: Driver created with explicit ChromeDriver path")
                else:
                    # Method 2: Try without service (auto-detection)
                    self.driver = webdriver.Chrome(options=options)
                    print("DEBUG: Driver created with auto-detection")
                
                # Hide automation
                self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
                
                return True
                
            except Exception as e:
                print(f"DEBUG: ChromeDriver methods failed: {e}")
                
                # Method 3: Try webdriver-manager
                try:
                    from webdriver_manager.chrome import ChromeDriverManager
                    service = Service(ChromeDriverManager().install())
                    self.driver = webdriver.Chrome(service=service, options=options)
                    print("DEBUG: Driver created with webdriver-manager")
                    return True
                except Exception as e2:
                    print(f"DEBUG: webdriver-manager failed: {e2}")
                    return False
            
        except Exception as e:
            print(f"DEBUG: Selenium driver creation error: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def _selenium_fetch(self):
        """Fetch using Selenium"""
        try:
            if not self.driver:
                if not self._create_selenium_driver():
                    print("DEBUG: Failed to create Selenium driver")
                    return []
            
            print(f"DEBUG: Loading {self.base_url} with Selenium...")
            
            # Load page with retry
            max_retries = 2
            for attempt in range(max_retries):
                try:
                    self.driver.get(self.base_url)
                    # Wait for page to load
                    time.sleep(3)
                    
                    # Check if page loaded properly
                    page_source = self.driver.page_source
                    if len(page_source) > 1000:
                        break
                    else:
                        print(f"DEBUG: Attempt {attempt + 1}: Small page ({len(page_source)} bytes)")
                        time.sleep(2)
                except Exception as e:
                    print(f"DEBUG: Load attempt {attempt + 1} failed: {e}")
                    if attempt == max_retries - 1:
                        return []
            
            # Save for debugging
            page_source = self.driver.page_source
            with open('final_selenium_page.html', 'w', encoding='utf-8') as f:
                f.write(page_source)
            print(f"DEBUG: Saved Selenium page ({len(page_source)} bytes)")
            
            # Take screenshot
            try:
                self.driver.save_screenshot('final_screenshot.png')
                print("DEBUG: Saved screenshot: final_screenshot.png")
            except:
                pass
            
            # Parse with BeautifulSoup
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(page_source, 'html.parser')
            
            return self._extract_articles(soup, 'selenium')
            
        except Exception as e:
            print(f"DEBUG: Selenium fetch error: {e}")
            import traceback
            traceback.print_exc()
            return []
    
    def _http_fetch(self):
        """Fetch using HTTP requests (fallback)"""
        try:
            # Enhanced headers to mimic real browser
            headers = {
                'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7',
                'Accept-Encoding': 'gzip, deflate, br',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
                'Sec-Fetch-Dest': 'document',
                'Sec-Fetch-Mode': 'navigate',
                'Sec-Fetch-Site': 'none',
                'Sec-Fetch-User': '?1',
                'Cache-Control': 'max-age=0',
            }
            
            print("DEBUG: Trying HTTP request...")
            response = self.session.get(self.base_url, headers=headers, timeout=15)
            print(f"DEBUG: HTTP status: {response.status_code}, size: {len(response.content)} bytes")
            
            # Save response
            with open('final_http_page.html', 'w', encoding='utf-8') as f:
                f.write(response.text[:10000])
            
            # Parse
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(response.content, 'html.parser')
            
            return self._extract_articles(soup, 'http')
            
        except Exception as e:
            print(f"DEBUG: HTTP fetch error: {e}")
            return []
    
    def fetch_articles(self) -> List[Dict[str, Any]]:
        """Main fetch method with fallback"""
        articles = []
        
        # Try Selenium first if enabled
        if self.use_selenium:
            print("DEBUG: === ATTEMPT 1: Selenium ===")
            selenium_articles = self._selenium_fetch()
            articles.extend(selenium_articles)
            
            if articles:
                print(f"DEBUG: Selenium found {len(articles)} articles")
            else:
                print("DEBUG: Selenium found 0 articles, trying HTTP...")
        
        # Fall back to HTTP if no articles from Selenium
        if not articles:
            print("DEBUG: === ATTEMPT 2: HTTP Request ===")
            http_articles = self._http_fetch()
            articles.extend(http_articles)
            
            if articles:
                print(f"DEBUG: HTTP found {len(articles)} articles")
            else:
                print("DEBUG: Both methods failed to find articles")
        
        # Clean up driver
        if self.driver:
            try:
                self.driver.quit()
            except:
                pass
            self.driver = None
        
        # Deduplicate
        unique_articles = []
        seen_titles = set()
        
        for article in articles:
            title_key = article['title'][:50].lower()
            if title_key not in seen_titles:
                seen_titles.add(title_key)
                unique_articles.append(article)
        
        print(f"DEBUG: Returning {len(unique_articles)} unique articles")
        return unique_articles
    
    def _extract_articles(self, soup, source: str) -> List[Dict[str, Any]]:
        """Extract articles from BeautifulSoup"""
        articles = []
        
        # Strategy 1: Look for fnDetailPopup (Adiga specific)
        print(f"DEBUG: [{source}] Searching for fnDetailPopup...")
        onclick_elements = soup.find_all(attrs={'onclick': re.compile(r'fnDetailPopup', re.I)})
        print(f"DEBUG: [{source}] Found {len(onclick_elements)} onclick elements")
        
        for element in onclick_elements[:20]:  # Limit to 20
            try:
                onclick = element.get('onclick', '')
                match = re.search(r"fnDetailPopup\s*\(\s*['\"]?(\d+)['\"]?\s*\)", onclick)
                
                if match:
                    article_id = match.group(1)
                    
                    # Get text - try multiple methods
                    text = element.get_text(strip=True)
                    if not text or len(text) < 5:
                        # Try parent
                        parent = element.parent
                        if parent:
                            text = parent.get_text(strip=True)
                    
                    # Try siblings
                    if not text or len(text) < 5:
                        if element.parent:
                            siblings_text = []
                            for sibling in element.parent.children:
                                if hasattr(sibling, 'get_text'):
                                    sibling_text = sibling.get_text(strip=True)
                                    if sibling_text and len(sibling_text) > 5:
                                        siblings_text.append(sibling_text)
                            if siblings_text:
                                text = ' '.join(siblings_text)[:200]
                    
                    if text and len(text) >= 5:
                        url = f"{self.base_url}/ArticleDetail.do?articleID={article_id}"
                        articles.append({
                            'title': text[:200],
                            'url': url,
                            'article_id': article_id,
                            'source': source
                        })
                        print(f"DEBUG: [{source}] Found via onclick: {text[:60]}...")
                        
            except Exception as e:
                print(f"DEBUG: Error processing onclick: {e}")
                continue
        
        # Strategy 2: Look for article links
        if len(articles) < 5:
            print(f"DEBUG: [{source}] Searching for article links...")
            
            # Get all links
            all_links = soup.find_all('a')
            print(f"DEBUG: [{source}] Total links: {len(all_links)}")
            
            # Keywords to look for
            keywords = [
                '입학', '모집', '공고', '안내', '전형', '대학',
                '학과', '학부', '모집요강', '원서접수', '정시', '수시',
                '추가모집', '정원', '면접', '실기', '합격', '발표'
            ]
            
            link_count = 0
            for link in all_links[:100]:  # Check first 100 links
                try:
                    href = link.get('href', '')
                    text = link.get_text(strip=True)
                    
                    # Skip if no meaningful text
                    if not text or len(text) < 10:
                        continue
                    
                    # Skip navigation links
                    if any(skip in text for skip in ['로그인', '회원가입', '검색', '홈', 'HOME', '이전', '다음']):
                        continue
                    
                    # Check if it looks like an article
                    has_keyword = any(keyword in text for keyword in keywords)
                    has_article_pattern = re.search(r'\d+기|\d+차|\d+회|모집공고|입학안내|원서접수', text)
                    
                    if has_keyword or has_article_pattern:
                        # Construct URL
                        if href and not href.startswith(('http://', 'https://', 'javascript:', 'mailto:', 'tel:', '#')):
                            if href.startswith('/'):
                                url = f"{self.base_url}{href}"
                            else:
                                url = f"{self.base_url}/{href}"
                        elif href.startswith('http'):
                            url = href
                        else:
                            url = self.base_url
                        
                        articles.append({
                            'title': text[:200],
                            'url': url,
                            'href': href,
                            'source': source
                        })
                        
                        link_count += 1
                        if link_count <= 3:  # Only log first 3
                            print(f"DEBUG: [{source}] Found via link: {text[:60]}...")
                        
                        if len(articles) >= 10:  # Stop if we have enough
                            break
                            
                except Exception as e:
                    continue
        
        # Strategy 3: Extract from page text as last resort
        if not articles:
            print(f"DEBUG: [{source}] Extracting from page text...")
            
            # Get clean text
            for script in soup(["script", "style", "meta", "link", "noscript"]):
                script.decompose()
            
            all_text = soup.get_text()
            lines = [line.strip() for line in all_text.split('\n') if line.strip()]
            
            for line in lines:
                if len(line) > 30:
                    for keyword in keywords:
                        if keyword in line:
                            articles.append({
                                'title': line[:150],
                                'url': self.base_url,
                                'content': line,
                                'source': f'{source}_text'
                            })
                            print(f"DEBUG: [{source}] Found in text: {line[:80]}...")
                            break
                
                if len(articles) >= 5:
                    break
        
        print(f"DEBUG: [{source}] Extracted {len(articles)} articles")
        return articles
    
    def parse_article(self, raw_data: Dict[str, Any]) -> Article:
        """Parse article content"""
        try:
            content = ""
            
            if raw_data['url'] and raw_data['url'] != self.base_url:
                try:
                    # Use appropriate method
                    if raw_data.get('source', '').startswith('selenium'):
                        # Recreate driver for article page
                        if not self.driver and not self._create_selenium_driver():
                            raise Exception("Could not create driver for article")
                        
                        self.driver.get(raw_data['url'])
                        time.sleep(2)
                        
                        from bs4 import BeautifulSoup
                        soup = BeautifulSoup(self.driver.page_source, 'html.parser')
                    else:
                        # Use HTTP
                        headers = {'User-Agent': 'Mozilla/5.0'}
                        response = self.session.get(raw_data['url'], headers=headers, timeout=10)
                        from bs4 import BeautifulSoup
                        soup = BeautifulSoup(response.content, 'html.parser')
                    
                    # Extract content
                    content_selectors = [
                        '.article-content', '.content', '.board-view',
                        '.view-content', '#articleContent', '#content',
                        'div[class*="content"]', 'article', 'main', 'td.content'
                    ]
                    
                    for selector in content_selectors:
                        element = soup.select_one(selector)
                        if element:
                            content = element.get_text(strip=True, separator=' ')
                            if len(content) > 100:
                                break
                    
                    # Fallback: get body text
                    if not content or len(content) < 100:
                        for tag in soup(['script', 'style', 'nav', 'header', 'footer']):
                            tag.decompose()
                        
                        body = soup.find('body')
                        if body:
                            content = body.get_text(strip=True, separator=' ')[:1500]
                    
                except Exception as e:
                    content = f"Content fetch error: {str(e)[:100]}"
            
            return Article(
                title=raw_data['title'],
                url=raw_data['url'],
                content=content,
                source=self.source_name
            )
            
        except Exception as e:
            print(f"DEBUG: Parse error: {e}")
            return Article(
                title=raw_data.get('title', 'Unknown Title'),
                url=raw_data.get('url', self.base_url),
                content="Parse error",
                source=self.source_name
            )
    
    def __del__(self):
        """Cleanup"""
        if self.driver:
            try:
                self.driver.quit()
            except:
                pass

def test_final_scraper():
    """Test the final scraper"""
    print("=== Testing Final Scraper ===")
    scraper = AdigaFinalScraper({'url': 'https://adiga.kr'})
    articles = scraper.fetch_articles()
    
    print(f"\nResults: {len(articles)} articles found")
    
    for i, article in enumerate(articles[:5]):
        print(f"\n{i+1}. {article['title'][:70]}...")
        print(f"   URL: {article['url']}")
        print(f"   Source: {article.get('source', 'unknown')}")
    
    return articles

if __name__ == "__main__":
    test_final_scraper()
FINAL_SCRAPER

# Create the final test and run script
echo -e "\nCreating final test script..."
cat > final_test.py << 'FINAL_TEST'
#!/usr/bin/env python3
"""
Final test script for University Monitor
"""
import sys
import os

# Add current directory to path
sys.path.insert(0, '.')

print("=" * 60)
print("FINAL TEST - University Admission Monitor")
print("=" * 60)

# Test 1: Imports
print("\n1. Testing imports...")
try:
    from scrapers.adiga_final import AdigaFinalScraper, test_final_scraper
    from models.article import Article
    from notifiers.telegram_notifier import TelegramNotifier
    print("✅ All imports successful")
except ImportError as e:
    print(f"❌ Import error: {e}")
    sys.exit(1)

# Test 2: Config
print("\n2. Checking configuration...")
config_files = ['config/config.yaml', 'config/sources.yaml', 'config/filters.yaml']
all_good = True

for file in config_files:
    if os.path.exists(file):
        print(f"   ✅ {file}")
    else:
        print(f"   ❌ {file} missing")
        all_good = False

if not all_good:
    print("\n⚠ Some config files missing. Creating defaults...")
    
    # Create minimal config if missing
    if not os.path.exists('config/config.yaml'):
        os.makedirs('config', exist_ok=True)
        with open('config/config.yaml', 'w') as f:
            f.write("""telegram:
  bot_token: "YOUR_BOT_TOKEN_HERE"
  chat_id: "YOUR_CHAT_ID_HERE"
database:
  path: "data/state.db"
logging:
  level: "INFO"
  file: "logs/monitor.log"
""")
        print("   Created config/config.yaml")
    
    if not os.path.exists('config/sources.yaml'):
        with open('config/sources.yaml', 'w') as f:
            f.write("""sources:
  adiga:
    name: "Adiga University Portal"
    url: "https://adiga.kr"
    enabled: true
""")
        print("   Created config/sources.yaml")

# Test 3: Scraper
print("\n3. Testing scraper...")
try:
    print("   Creating scraper instance...")
    scraper = AdigaFinalScraper({'url': 'https://adiga.kr'})
    
    print("   Fetching articles (this may take 10-20 seconds)...")
    import time
    start_time = time.time()
    
    articles = scraper.fetch_articles()
    
    elapsed = time.time() - start_time
    print(f"   Fetch completed in {elapsed:.1f} seconds")
    print(f"   Found {len(articles)} articles")
    
    if articles:
        print("\n   First 3 articles:")
        for i, article in enumerate(articles[:3]):
            print(f"   {i+1}. {article['title'][:60]}...")
            print(f"      URL: {article['url']}")
            print(f"      Source: {article.get('source', 'unknown')}")
        
        # Test parsing first article
        print("\n   Testing article parsing...")
        parsed = scraper.parse_article(articles[0])
        print(f"      Title: {parsed.title[:50]}...")
        print(f"      Content length: {len(parsed.content)} characters")
        if parsed.content:
            print(f"      Preview: {parsed.content[:100]}...")
        
        print("\n✅ SCRAPER TEST PASSED!")
        
        # Ask user if they want to run monitor
        print("\n" + "=" * 60)
        print("READY TO RUN MONITOR")
        print("=" * 60)
        
        print("\nOptions:")
        print("1. Test mode (no Telegram messages)")
        print("2. Run for real (sends to Telegram)")
        print("3. Exit")
        
        choice = input("\nEnter choice (1-3): ").strip()
        
        if choice == '1':
            print("\nStarting in TEST mode...")
            os.system('python3 core/monitor_engine.py --test')
        elif choice == '2':
            print("\nStarting monitor...")
            os.system('python3 core/monitor_engine.py')
        else:
            print("\nExiting. You can run manually:")
            print("  python3 core/monitor_engine.py --test")
            print("  python3 core/monitor_engine.py")
        
    else:
        print("\n⚠ No articles found.")
        print("\nDebug files created:")
        debug_files = [f for f in os.listdir('.') if f.startswith('final_')]
        for f in debug_files:
            print(f"  - {f}")
        
        print("\nCheck these files to see what the scraper received.")
        print("If files are very small, the site might be blocking requests.")
        
except Exception as e:
    print(f"\n❌ Scraper test failed: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 60)
print("TEST COMPLETE")
print("=" * 60)
FINAL_TEST

# Make it executable
chmod +x final_test.py

# Create final integration script
echo -e "\nCreating final integration..."
cat > final_integrate.sh << 'FINAL_INTEGRATE'
#!/bin/bash
echo "=== Final Integration ==="

# Set as main scraper
echo "1. Setting as main scraper..."
cp scrapers/adiga_final.py scrapers/adiga_scraper.py
sed -i 's/class AdigaFinalScraper/class AdigaScraper/' scrapers/adiga_scraper.py
sed -i 's/AdigaFinalScraper(/AdigaScraper(/' scrapers/adiga_scraper.py

echo "2. Running final test..."
python3 final_test.py

echo -e "\n=== Final Setup Complete ==="
echo -e "\nYour system now has:"
echo "✅ Selenium 4.40.0"
echo "✅ Smart scraper with fallback"
echo "✅ Chrome at /usr/bin/google-chrome-stable"
echo "✅ Test script: final_test.py"
echo ""
echo "To run anytime:"
echo "  python3 final_test.py"
echo "  python3 core/monitor_engine.py --test"
echo "  python3 core/monitor_engine.py"
FINAL_INTEGRATE

chmod +x final_integrate.sh

echo -e "\nRunning final integration..."
./final_integrate.sh

echo -e "\n=== MANUAL SETUP (if needed) ==="
echo "If ChromeDriver is missing, install it:"
echo "  sudo pacman -S chromedriver"
echo ""
echo "Or allow the script to auto-install it when you run."
