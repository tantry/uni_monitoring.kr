"""
Working Adiga scraper - tries multiple approaches
"""
import time
import re
import random
from typing import List, Dict, Any
from core.base_scraper import BaseScraper
from models.article import Article

class AdigaWorkingScraper(BaseScraper):
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.source_name = "adiga"
        
        # Enhanced headers to avoid blocking
        self.session.headers.update({
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
        })
    
    def get_source_name(self) -> str:
        return self.source_name
    
    def fetch_articles(self) -> List[Dict[str, Any]]:
        """Main method to fetch articles"""
        print(f"DEBUG: Starting fetch from {self.base_url}")
        
        # Try multiple approaches
        approaches = [
            self._try_standard_request,
            self._try_with_cookies,
            self._try_different_paths,
            self._try_google_cache,
        ]
        
        all_articles = []
        
        for approach in approaches:
            try:
                print(f"DEBUG: Trying {approach.__name__}...")
                articles = approach()
                
                if articles:
                    print(f"DEBUG: Found {len(articles)} articles with {approach.__name__}")
                    all_articles.extend(articles)
                    
                    # If we found articles, we can stop trying other methods
                    if len(all_articles) >= 3:
                        break
                        
            except Exception as e:
                print(f"DEBUG: {approach.__name__} failed: {e}")
                continue
        
        # Deduplicate
        unique_articles = []
        seen_urls = set()
        
        for article in all_articles:
            if article['url'] not in seen_urls:
                seen_urls.add(article['url'])
                unique_articles.append(article)
        
        print(f"DEBUG: Returning {len(unique_articles)} unique articles")
        return unique_articles
    
    def _try_standard_request(self) -> List[Dict[str, Any]]:
        """Standard request approach"""
        try:
            response = self.session.get(self.base_url, timeout=15)
            print(f"DEBUG: Status {response.status_code}, Size: {len(response.content)}")
            
            # Save response for debugging
            with open('debug_last_response.html', 'w', encoding='utf-8') as f:
                f.write(response.text[:5000])  # Save first 5000 chars
            
            # Check response
            if len(response.content) < 500:
                print(f"DEBUG: Response too small, might be blocked")
                return []
            
            return self._parse_response(response)
            
        except Exception as e:
            print(f"DEBUG: Standard request error: {e}")
            return []
    
    def _try_with_cookies(self) -> List[Dict[str, Any]]:
        """Try with initial cookies setup"""
        try:
            # First request to get cookies
            self.session.get(self.base_url, timeout=10)
            time.sleep(1)
            
            # Second request with cookies
            response = self.session.get(self.base_url, timeout=15)
            return self._parse_response(response)
            
        except Exception as e:
            print(f"DEBUG: Cookies approach error: {e}")
            return []
    
    def _try_different_paths(self) -> List[Dict[str, Any]]:
        """Try different URL paths"""
        paths = [
            '/',
            '/index.php',
            '/main.php',
            '/board/list.php',
            '/bbs/board.php',
            '/Article/List.do',
            '/news/list.php',
        ]
        
        for path in paths:
            try:
                url = f"{self.base_url}{path}"
                print(f"DEBUG: Trying path: {url}")
                
                response = self.session.get(url, timeout=10)
                articles = self._parse_response(response)
                
                if articles:
                    return articles
                    
            except Exception as e:
                print(f"DEBUG: Path {path} error: {e}")
                continue
        
        return []
    
    def _try_google_cache(self) -> List[Dict[str, Any]]:
        """Try Google Cache as last resort"""
        try:
            cache_url = f"https://webcache.googleusercontent.com/search?q=cache:{self.base_url}"
            response = self.session.get(cache_url, timeout=15)
            
            if response.status_code == 200:
                return self._parse_response(response, source='google_cache')
        except:
            pass
        
        return []
    
    def _parse_response(self, response, source='direct') -> List[Dict[str, Any]]:
        """Parse response into articles"""
        from bs4 import BeautifulSoup
        
        articles = []
        
        try:
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Method 1: Look for onclick with fnDetailPopup
            onclick_elements = soup.find_all(attrs={'onclick': re.compile(r'fnDetailPopup', re.I)})
            print(f"DEBUG: Found {len(onclick_elements)} onclick elements")
            
            for element in onclick_elements:
                try:
                    onclick = element.get('onclick', '')
                    match = re.search(r"fnDetailPopup\s*\(\s*['\"]?(\d+)['\"]?\s*\)", onclick)
                    
                    if match:
                        article_id = match.group(1)
                        text = element.get_text(strip=True)
                        
                        if not text or len(text) < 5:
                            # Try to get text from parent or siblings
                            parent = element.parent
                            if parent:
                                text = parent.get_text(strip=True)
                        
                        if text and len(text) >= 5:
                            url = f"{self.base_url}/ArticleDetail.do?articleID={article_id}"
                            
                            articles.append({
                                'title': text[:200],
                                'url': url,
                                'article_id': article_id,
                                'source': source
                            })
                            
                            print(f"DEBUG: Found via onclick: {text[:50]}...")
                except Exception as e:
                    print(f"DEBUG: Error processing onclick: {e}")
                    continue
            
            # Method 2: Look for article links
            if len(articles) < 3:
                # Common patterns in Korean university sites
                patterns = [
                    r'article', r'news', r'board', r'공지', r'공고', 
                    r'입학', r'모집', r'안내', r'\d+기', r'\d+차'
                ]
                
                all_links = soup.find_all('a')
                print(f"DEBUG: Total links found: {len(all_links)}")
                
                for link in all_links[:100]:  # Check first 100 links
                    try:
                        href = link.get('href', '')
                        text = link.get_text(strip=True)
                        
                        # Skip if no meaningful text
                        if not text or len(text) < 10:
                            continue
                        
                        # Skip navigation links
                        if any(skip in text for skip in ['로그인', '회원가입', '검색', 'HOME', '홈']):
                            continue
                        
                        # Check if it looks like an article
                        looks_like_article = any(
                            pattern in text.lower() or 
                            re.search(r'\d{4}년|\d+월|\d+일|모집공고|입학안내', text)
                            for pattern in ['입학', '모집', '공고', '안내', '대학']
                        )
                        
                        if looks_like_article:
                            # Construct URL
                            url = self._construct_url(href)
                            
                            articles.append({
                                'title': text[:200],
                                'url': url,
                                'href': href,
                                'source': source
                            })
                            
                            print(f"DEBUG: Found via link text: {text[:50]}...")
                            
                    except Exception as e:
                        continue
            
            # Method 3: Extract from page text
            if not articles:
                print("DEBUG: Extracting from page text...")
                
                # Get all text
                for script in soup(["script", "style", "meta", "link"]):
                    script.decompose()
                
                all_text = soup.get_text()
                lines = [line.strip() for line in all_text.split('\n') if line.strip()]
                
                # Look for university-related lines
                keywords = ['입학', '모집', '공고', '안내', '대학', '학과', '모집요강']
                
                for line in lines:
                    if len(line) > 20:
                        for keyword in keywords:
                            if keyword in line:
                                articles.append({
                                    'title': line[:150],
                                    'url': self.base_url,
                                    'content': line,
                                    'source': f'{source}_text'
                                })
                                print(f"DEBUG: Found in text: {line[:60]}...")
                                break
                    
                    if len(articles) >= 5:
                        break
            
        except Exception as e:
            print(f"DEBUG: Parse error: {e}")
        
        return articles
    
    def _construct_url(self, href: str) -> str:
        """Construct full URL from href"""
        if not href or href.startswith('javascript:'):
            return self.base_url
        
        if href.startswith('http://') or href.startswith('https://'):
            return href
        
        if href.startswith('/'):
            return f"{self.base_url}{href}"
        
        return f"{self.base_url}/{href}"
    
    def parse_article(self, raw_data: Dict[str, Any]) -> Article:
        """Parse article content"""
        try:
            content = ""
            
            # Only try to fetch content if URL is not the base URL
            if raw_data['url'] and raw_data['url'] != self.base_url:
                try:
                    print(f"DEBUG: Fetching article content: {raw_data['url']}")
                    response = self.session.get(raw_data['url'], timeout=10)
                    
                    if response.status_code == 200:
                        from bs4 import BeautifulSoup
                        soup = BeautifulSoup(response.content, 'html.parser')
                        
                        # Try to find content
                        for tag in soup(['script', 'style', 'nav', 'header', 'footer']):
                            tag.decompose()
                        
                        content = soup.get_text(strip=True, separator=' ')[:1000]
                        
                        # Save for debugging
                        with open('debug_article.html', 'w', encoding='utf-8') as f:
                            f.write(response.text[:3000])
                except Exception as e:
                    content = f"Content fetch error: {str(e)[:100]}"
            
            return Article(
                title=raw_data['title'],
                url=raw_data['url'],
                content=content,
                source=self.source_name,
                published_date=time.strftime('%Y-%m-%d %H:%M:%S')
            )
            
        except Exception as e:
            print(f"DEBUG: Article parse error: {e}")
            return Article(
                title=raw_data.get('title', 'No Title'),
                url=raw_data.get('url', self.base_url),
                content="Parse error",
                source=self.source_name
            )

def test_scraper():
    """Test function"""
    scraper = AdigaWorkingScraper({'url': 'https://www.adiga.kr'})
    articles = scraper.fetch_articles()
    
    print(f"\nTest Results:")
    print(f"Found {len(articles)} articles")
    
    for i, article in enumerate(articles[:5]):
        print(f"\n{i+1}. {article['title'][:60]}...")
        print(f"   URL: {article['url']}")
    
    return articles

if __name__ == "__main__":
    test_scraper()
