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
