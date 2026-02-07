"""
Adiga scraper that handles JavaScript redirects
"""
import time
import re
import requests
from typing import List, Dict, Any
from core.base_scraper import BaseScraper
from models.article import Article

class AdigaJsRedirectScraper(BaseScraper):
    def __init__(self, config: Dict[str, Any]):
        # Set to desktop URL directly
        config['url'] = "https://www.adiga.kr"
        self.desktop_path = "/man/inf/mainView.do?menuId=PCMANINF1000"
        self.mobile_url = "https://m.adiga.kr"
        
        super().__init__(config)
        self.source_name = "adiga"
        self.actual_content_url = None
        
        # Enhanced headers
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7',
        })
    
    def get_source_name(self) -> str:
        return self.source_name
    
    def _get_actual_content(self):
        """Get the actual content by following JavaScript redirects"""
        # Strategy 1: Try desktop URL directly
        desktop_url = f"{self.base_url}{self.desktop_path}"
        print(f"DEBUG: Trying desktop URL: {desktop_url}")
        
        try:
            response = self.session.get(desktop_url, timeout=15)
            print(f"DEBUG: Desktop response: {response.status_code}, {len(response.content)} bytes")
            
            if response.status_code == 200 and len(response.content) > 1000:
                self.actual_content_url = desktop_url
                return response
        except Exception as e:
            print(f"DEBUG: Desktop URL failed: {e}")
        
        # Strategy 2: Try mobile URL
        print(f"DEBUG: Trying mobile URL: {self.mobile_url}")
        try:
            response = self.session.get(self.mobile_url, timeout=15)
            print(f"DEBUG: Mobile response: {response.status_code}, {len(response.content)} bytes")
            
            if response.status_code == 200 and len(response.content) > 1000:
                self.actual_content_url = self.mobile_url
                return response
        except Exception as e:
            print(f"DEBUG: Mobile URL failed: {e}")
        
        # Strategy 3: Try Selenium if available
        print("DEBUG: Trying Selenium for JavaScript execution...")
        selenium_response = self._try_selenium()
        if selenium_response:
            return selenium_response
        
        return None
    
    def _try_selenium(self):
        """Try Selenium to execute JavaScript"""
        try:
            from selenium import webdriver
            from selenium.webdriver.chrome.options import Options
            
            print("DEBUG: Initializing Selenium...")
            options = Options()
            options.add_argument('--headless')
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
            
            driver = webdriver.Chrome(options=options)
            
            # Load the page and let JavaScript execute
            print(f"DEBUG: Loading {self.base_url} with Selenium...")
            driver.get(self.base_url)
            time.sleep(3)  # Wait for JavaScript
            
            # Get the final URL after JavaScript redirects
            final_url = driver.current_url
            page_source = driver.page_source
            
            print(f"DEBUG: Final URL after JS: {final_url}")
            print(f"DEBUG: Page size: {len(page_source)} bytes")
            
            driver.quit()
            
            if len(page_source) > 1000:
                self.actual_content_url = final_url
                # Create a mock response object
                class MockResponse:
                    def __init__(self, url, content):
                        self.url = url
                        self.content = content.encode('utf-8') if isinstance(content, str) else content
                        self.status_code = 200
                        self.text = content if isinstance(content, str) else content.decode('utf-8', errors='ignore')
                
                return MockResponse(final_url, page_source)
            
        except Exception as e:
            print(f"DEBUG: Selenium failed: {e}")
        
        return None
    
    def fetch_articles(self) -> List[Dict[str, Any]]:
        """Main fetch method"""
        print("=== Adiga JavaScript Redirect Scraper ===")
        
        # Get actual content
        response = self._get_actual_content()
        
        if not response:
            print("DEBUG: Could not get actual content")
            return []
        
        print(f"DEBUG: Using content from: {self.actual_content_url}")
        print(f"DEBUG: Content size: {len(response.content)} bytes")
        
        # Save for analysis
        with open('actual_adiga_content_final.html', 'w', encoding='utf-8') as f:
            f.write(response.text[:20000])
        
        # Parse content
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Remove scripts/styles
        for script in soup(["script", "style"]):
            script.decompose()
        
        # Save cleaned version
        with open('cleaned_adiga_final.html', 'w', encoding='utf-8') as f:
            f.write(soup.prettify()[:10000])
        
        # Extract articles
        articles = self._extract_articles(soup)
        print(f"DEBUG: Found {len(articles)} articles")
        
        return articles
    
    def _extract_articles(self, soup) -> List[Dict[str, Any]]:
        """Extract articles from the actual content"""
        articles = []
        
        # First, let's understand the page structure
        print("DEBUG: Analyzing page structure...")
        
        # Look for common Korean site structures
        # 1. Tables (common in Korean sites)
        tables = soup.find_all('table')
        print(f"DEBUG: Found {len(tables)} tables")
        
        # 2. List items
        lists = soup.find_all(['ul', 'ol'])
        print(f"DEBUG: Found {len(lists)} lists")
        
        # 3. Divs with common class names
        common_classes = ['board', 'list', 'article', 'news', 'content', 'bbs']
        for cls in common_classes:
            elements = soup.find_all(class_=re.compile(cls, re.I))
            if elements:
                print(f"DEBUG: Found {len(elements)} elements with class containing '{cls}'")
        
        # 4. Look for fnDetailPopup
        onclick_elements = soup.find_all(attrs={'onclick': re.compile(r'fnDetailPopup', re.I)})
        print(f"DEBUG: Found {len(onclick_elements)} fnDetailPopup elements")
        
        for i, element in enumerate(onclick_elements[:20]):
            try:
                onclick = element.get('onclick', '')
                match = re.search(r"fnDetailPopup\s*\(\s*['\"]?(\d+)['\"]?\s*\)", onclick)
                
                if match:
                    article_id = match.group(1)
                    text = element.get_text(strip=True)
                    
                    if not text or len(text) < 5:
                        parent = element.parent
                        if parent:
                            text = parent.get_text(strip=True)
                    
                    if text and len(text) >= 5:
                        # Determine base URL for article links
                        base = self.actual_content_url or self.base_url
                        if 'www.adiga.kr' in base:
                            url = f"https://www.adiga.kr/ArticleDetail.do?articleID={article_id}"
                        elif 'm.adiga.kr' in base:
                            url = f"https://m.adiga.kr/ArticleDetail.do?articleID={article_id}"
                        else:
                            url = f"{self.base_url}/ArticleDetail.do?articleID={article_id}"
                        
                        articles.append({
                            'title': text[:200],
                            'url': url,
                            'article_id': article_id,
                            'source': 'fnDetailPopup'
                        })
                        print(f"DEBUG: Found via fnDetailPopup: {text[:50]}...")
                        
            except Exception as e:
                print(f"DEBUG: Error processing onclick: {e}")
                continue
        
        # If no fnDetailPopup found, try to find any article-like content
        if not articles:
            print("DEBUG: Searching for any article-like content...")
            
            # Get all links
            all_links = soup.find_all('a')
            print(f"DEBUG: Total links: {len(all_links)}")
            
            for i, link in enumerate(all_links[:200]):
                try:
                    href = link.get('href', '')
                    text = link.get_text(strip=True)
                    
                    # Filter criteria
                    if not text or len(text) < 10:
                        continue
                    
                    # Skip navigation
                    skip_terms = ['로그인', '회원가입', '검색', '홈', 'HOME', '이전', '다음']
                    if any(term in text for term in skip_terms):
                        continue
                    
                    # Must have university keywords
                    keywords = ['입학', '모집', '공고', '안내', '대학', '학과', '학부']
                    if any(keyword in text for keyword in keywords):
                        # Build URL
                        base = self.actual_content_url or self.base_url
                        url = self._build_url(href, base)
                        
                        articles.append({
                            'title': text[:200],
                            'url': url,
                            'href': href,
                            'source': 'link'
                        })
                        
                        if len(articles) <= 5:  # Only log first 5
                            print(f"DEBUG [{i+1}]: Article link: {text[:50]}...")
                        
                except:
                    continue
        
        # If still no articles, look for text content
        if not articles:
            print("DEBUG: Extracting from page text...")
            all_text = soup.get_text()
            lines = [line.strip() for line in all_text.split('\n') if line.strip()]
            
            for line in lines:
                if len(line) > 30:
                    for keyword in ['입학', '모집', '공고', '안내']:
                        if keyword in line:
                            articles.append({
                                'title': line[:150],
                                'url': self.actual_content_url or self.base_url,
                                'content': line,
                                'source': 'text'
                            })
                            print(f"DEBUG: Found in text: {line[:80]}...")
                            break
                
                if len(articles) >= 3:
                    break
        
        # Last resort: mock data for testing
        if not articles:
            print("DEBUG: Using mock data for testing...")
            articles = self._get_mock_articles()
        
        return articles
    
    def _build_url(self, href: str, base_url: str) -> str:
        """Build absolute URL"""
        if not href or href.startswith('javascript:'):
            return base_url
        
        if href.startswith('http://') or href.startswith('https://'):
            return href
        
        if href.startswith('/'):
            # Extract domain from base_url
            from urllib.parse import urlparse
            parsed = urlparse(base_url)
            domain = f"{parsed.scheme}://{parsed.netloc}"
            return f"{domain}{href}"
        
        # Relative URL
        if base_url.endswith('/'):
            return f"{base_url}{href}"
        else:
            return f"{base_url}/{href}"
    
    def _get_mock_articles(self):
        """Get mock articles for testing"""
        return [
            {
                'title': '[테스트] 서울대학교 음악학과 2026학년도 추가모집 공고',
                'url': 'https://www.adiga.kr/ArticleDetail.do?articleID=99999',
                'content': '서울대학교 음악학과에서 2026학년도 추가모집을 실시합니다. 접수기간: 2026.02.10~02.20'
            },
            {
                'title': '[테스트] 연세대학교 영어영문학과 정시모집 안내',
                'url': 'https://www.adiga.kr/ArticleDetail.do?articleID=99998', 
                'content': '연세대학교 영어영문학과 2026학년도 정시모집 안내입니다. 모집인원: 30명'
            },
            {
                'title': '[테스트] 고려대학교 한국어학과 수시모집 공고',
                'url': 'https://www.adiga.kr/ArticleDetail.do?articleID=99997',
                'content': '고려대학교 한국어학과 2026학년도 수시모집 모집요강 안내'
            }
        ]
    
    def parse_article(self, raw_data: Dict[str, Any]) -> Article:
        """Parse article"""
        try:
            content = raw_data.get('content', '')
            
            # Try to fetch real content if not provided
            if not content and raw_data['url']:
                try:
                    response = self.session.get(raw_data['url'], timeout=10)
                    if response.status_code == 200:
                        from bs4 import BeautifulSoup
                        soup = BeautifulSoup(response.content, 'html.parser')
                        
                        for tag in soup(['script', 'style']):
                            tag.decompose()
                        
                        content = soup.get_text(strip=True, separator=' ')[:1000]
                except:
                    content = "내용을 불러올 수 없습니다."
            
            return Article(
                title=raw_data['title'],
                url=raw_data['url'],
                content=content,
                source=self.source_name
            )
            
        except Exception as e:
            print(f"DEBUG: Parse error: {e}")
            return Article(
                title=raw_data.get('title', 'Unknown'),
                url=raw_data.get('url', self.base_url),
                content="Parse error",
                source=self.source_name
            )

def test_js_redirect_scraper():
    """Test the scraper"""
    print("=" * 60)
    print("ADIGA JAVASCRIPT REDIRECT SCRAPER TEST")
    print("=" * 60)
    
    scraper = AdigaJsRedirectScraper({'url': 'https://www.adiga.kr'})
    articles = scraper.fetch_articles()
    
    print(f"\n✅ FINAL: {len(articles)} articles found")
    
    for i, article in enumerate(articles):
        print(f"\n{i+1}. {article['title'][:80]}...")
        print(f"   URL: {article['url']}")
        print(f"   Source: {article.get('source', 'unknown')}")
    
    # Test parsing
    if articles:
        print("\n" + "=" * 60)
        print("ARTICLE PARSING TEST:")
        print("=" * 60)
        
        parsed = scraper.parse_article(articles[0])
        print(f"\nTitle: {parsed.title}")
        print(f"URL: {parsed.url}")
        print(f"Content: {parsed.content[:200]}...")
        
        # Show Telegram message format
        message = f"""
🎓 <b>새 입학 공고</b>

<b>제목:</b> {parsed.title}

<b>내용:</b> {parsed.content[:200]}...

<b>링크:</b> {parsed.url}

<b>출처:</b> {parsed.source}
#adiga #대학입시
"""
        print(f"\nTelegram message:\n{message}")
    
    return articles

if __name__ == "__main__":
    test_js_redirect_scraper()
