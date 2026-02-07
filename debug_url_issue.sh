#!/bin/bash
echo "=== Debugging URL Issue ==="

# First, let's test the site manually
echo "1. Testing Adiga.kr manually..."
curl -s "https://adiga.kr" -o debug_adiga_raw.html
echo "Raw response size: $(wc -c < debug_adiga_raw.html) bytes"
echo "First 500 characters:"
head -c 500 debug_adiga_raw.html
echo -e "\n..."

# Check for redirects
echo -e "\n2. Checking for redirects..."
curl -I "https://adiga.kr" 2>/dev/null | grep -i "location\|http"

# Create a minimal test to reproduce the issue
echo -e "\n3. Creating minimal test..."
cat > test_url_issue.py << 'TESTURL'
import requests
from bs4 import BeautifulSoup

print("=== Testing URL Issue ===")

# Test with different session setups
test_cases = [
    {
        'name': 'Default session',
        'session': requests.Session(),
        'headers': {}
    },
    {
        'name': 'Session with headers',
        'session': requests.Session(),
        'headers': {
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'
        }
    }
]

url = "https://adiga.kr"

for test in test_cases:
    print(f"\n--- {test['name']} ---")
    session = test['session']
    
    if test['headers']:
        session.headers.update(test['headers'])
    
    try:
        print(f"Fetching {url}...")
        response = session.get(url, timeout=10)
        print(f"Status: {response.status_code}")
        print(f"Content length: {len(response.content)} bytes")
        
        # Save the response
        filename = f"debug_{test['name'].replace(' ', '_').lower()}.html"
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(response.text)
        print(f"Saved to: {filename}")
        
        # Parse with BeautifulSoup
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Check for links
        links = soup.find_all('a')
        print(f"Total links found: {len(links)}")
        
        # Show first 5 links with href
        print("\nFirst 5 links with href:")
        count = 0
        for link in links:
            href = link.get('href', '')
            text = link.get_text(strip=True)
            if href:
                print(f"  Text: {text[:30]}...")
                print(f"  Href: {href}")
                count += 1
                if count >= 5:
                    break
        
        # Check for onclick with fnDetailPopup
        print("\nChecking for fnDetailPopup...")
        onclick_elements = soup.find_all(attrs={'onclick': True})
        fn_detail_count = 0
        for element in onclick_elements:
            onclick = element.get('onclick', '')
            if 'fnDetailPopup' in onclick:
                fn_detail_count += 1
                if fn_detail_count <= 3:
                    text = element.get_text(strip=True)
                    print(f"  Found: {onclick[:50]}...")
                    print(f"  Text: {text[:30]}...")
        
        print(f"Total fnDetailPopup elements: {fn_detail_count}")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

print("\n=== Checking base_scraper session ===")
try:
    from core.base_scraper import BaseScraper
    
    class TestScraper(BaseScraper):
        def get_source_name(self):
            return 'test'
        
        def fetch_articles(self):
            return []
        
        def parse_article(self, raw_data):
            return None
    
    scraper = TestScraper({'url': 'https://adiga.kr'})
    print(f"Scraper session headers: {dict(scraper.session.headers)}")
    
    # Try to fetch
    try:
        response = scraper.session.get('https://adiga.kr', timeout=10)
        print(f"BaseScraper session status: {response.status_code}")
        print(f"Content length: {len(response.content)} bytes")
    except Exception as e:
        print(f"BaseScraper session error: {e}")
        
except ImportError as e:
    print(f"Could not import BaseScraper: {e}")

print("\n=== Debug Complete ===")
TESTURL

python3 test_url_issue.py

echo -e "\n4. Creating a fixed scraper..."
cat > scrapers/adiga_fixed.py << 'FIXED'
"""
Fixed Adiga scraper - resolves the empty URL issue
"""
import time
import re
import requests
from typing import List, Dict, Any
from core.base_scraper import BaseScraper
from models.article import Article

class AdigaFixedScraper(BaseScraper):
    def __init__(self, config: Dict[str, Any]):
        # Don't call parent __init__ yet
        self.config = config
        self.source_name = "adiga"
        self.base_url = config.get('url', 'https://adiga.kr')
        
        # Create a fresh session with proper headers
        self.session = requests.Session()
        self._setup_session()
        
        self.logger = None  # Will be setup later
    
    def _setup_session(self):
        """Setup session with proper headers"""
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
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
        self.session.headers.update(headers)
        
        # Add retry adapter
        from requests.adapters import HTTPAdapter
        from urllib3.util.retry import Retry
        
        retry_strategy = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("https://", adapter)
        self.session.mount("http://", adapter)
    
    def get_source_name(self) -> str:
        return self.source_name
    
    def fetch_articles(self) -> List[Dict[str, Any]]:
        """Fetch articles - simple and reliable"""
        print(f"DEBUG: Starting fetch from {self.base_url}")
        
        try:
            # Fetch the page
            print(f"DEBUG: Sending request...")
            response = self.session.get(self.base_url, timeout=15)
            print(f"DEBUG: Response: {response.status_code}, {len(response.content)} bytes")
            
            # Save for debugging
            with open('debug_fixed_response.html', 'w', encoding='utf-8') as f:
                f.write(response.text)
            print(f"DEBUG: Saved response to debug_fixed_response.html")
            
            # Check if we got content
            if len(response.content) < 1000:
                print(f"DEBUG: Small response, might be blocking or redirect")
                return []
            
            # Parse with BeautifulSoup
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(response.content, 'html.parser')
            
            articles = []
            
            # Method 1: Look for onclick with fnDetailPopup
            print("DEBUG: Looking for fnDetailPopup...")
            onclick_elements = soup.find_all(attrs={'onclick': re.compile(r'fnDetailPopup', re.I)})
            print(f"DEBUG: Found {len(onclick_elements)} onclick elements")
            
            for element in onclick_elements[:20]:  # Limit to 20
                try:
                    onclick = element.get('onclick', '')
                    match = re.search(r"fnDetailPopup\s*\(\s*['\"]?(\d+)['\"]?\s*\)", onclick)
                    
                    if match:
                        article_id = match.group(1)
                        text = element.get_text(strip=True)
                        
                        if not text or len(text) < 5:
                            # Try to get text from surrounding elements
                            parent = element.parent
                            if parent:
                                text = parent.get_text(strip=True)
                        
                        if text and len(text) >= 5:
                            url = f"{self.base_url}/ArticleDetail.do?articleID={article_id}"
                            articles.append({
                                'title': text[:200],
                                'url': url,
                                'article_id': article_id,
                                'onclick': onclick[:100]
                            })
                            print(f"DEBUG: Found via onclick: {text[:50]}...")
                            
                except Exception as e:
                    print(f"DEBUG: Error processing onclick: {e}")
                    continue
            
            # Method 2: Look for article links
            if len(articles) < 3:
                print("DEBUG: Looking for article links...")
                
                # Get all links
                all_links = soup.find_all('a')
                print(f"DEBUG: Total links: {len(all_links)}")
                
                for link in all_links[:100]:  # Check first 100
                    try:
                        href = link.get('href', '')
                        text = link.get_text(strip=True)
                        
                        # Skip if no meaningful text
                        if not text or len(text) < 10:
                            continue
                        
                        # Skip navigation links
                        skip_terms = ['로그인', '회원가입', '검색', '홈', 'HOME', '이전', '다음']
                        if any(term in text for term in skip_terms):
                            continue
                        
                        # Check if it looks like an article
                        keywords = ['입학', '모집', '공고', '안내', '대학', '학과']
                        if any(keyword in text for keyword in keywords):
                            # Construct URL properly
                            url = self._construct_url(href)
                            
                            articles.append({
                                'title': text[:200],
                                'url': url,
                                'href': href
                            })
                            print(f"DEBUG: Found via link: {text[:50]}...")
                            
                    except Exception as e:
                        continue
            
            # Method 3: Extract from page text
            if not articles:
                print("DEBUG: Extracting from page text...")
                
                # Get all text
                for script in soup(["script", "style"]):
                    script.decompose()
                
                all_text = soup.get_text()
                lines = [line.strip() for line in all_text.split('\n') if line.strip()]
                
                for line in lines:
                    if len(line) > 30:
                        if any(keyword in line for keyword in ['입학', '모집', '공고', '안내']):
                            articles.append({
                                'title': line[:150],
                                'url': self.base_url,
                                'content': line
                            })
                            print(f"DEBUG: Found in text: {line[:80]}...")
                            break
            
            print(f"DEBUG: Total articles found: {len(articles)}")
            return articles
            
        except Exception as e:
            print(f"DEBUG: Fetch error: {e}")
            import traceback
            traceback.print_exc()
            return []
    
    def _construct_url(self, href: str) -> str:
        """Construct full URL from href - handles empty and relative URLs"""
        if not href or href.strip() == '':
            return self.base_url
        
        if href.startswith('javascript:'):
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
            
            if raw_data['url'] and raw_data['url'] != self.base_url:
                try:
                    print(f"DEBUG: Fetching article: {raw_data['url']}")
                    response = self.session.get(raw_data['url'], timeout=10)
                    
                    if response.status_code == 200:
                        from bs4 import BeautifulSoup
                        soup = BeautifulSoup(response.content, 'html.parser')
                        
                        # Get content
                        for tag in soup(['script', 'style', 'nav', 'header', 'footer']):
                            tag.decompose()
                        
                        content = soup.get_text(strip=True, separator=' ')[:1000]
                        
                        # Save for debugging
                        with open('debug_article_content.html', 'w', encoding='utf-8') as f:
                            f.write(response.text[:3000])
                except Exception as e:
                    content = f"Error: {str(e)[:100]}"
            
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

def test_fixed_scraper():
    """Test the fixed scraper"""
    print("=== Testing Fixed Scraper ===")
    scraper = AdigaFixedScraper({'url': 'https://adiga.kr'})
    articles = scraper.fetch_articles()
    
    print(f"\nResults: {len(articles)} articles found")
    
    for i, article in enumerate(articles[:5]):
        print(f"\n{i+1}. {article['title'][:70]}...")
        print(f"   URL: {article['url']}")
    
    # Test parsing
    if articles:
        print("\nTesting article parsing...")
        parsed = scraper.parse_article(articles[0])
        print(f"Title: {parsed.title[:50]}...")
        print(f"Content length: {len(parsed.content)} chars")
    
    return articles

if __name__ == "__main__":
    test_fixed_scraper()
FIXED

echo -e "\n5. Testing the fixed scraper..."
python3 -c "
import sys
sys.path.insert(0, '.')
try:
    from scrapers.adiga_fixed import test_fixed_scraper
    test_fixed_scraper()
except Exception as e:
    print(f'Error: {e}')
    import traceback
    traceback.print_exc()
"

echo -e "\n=== Debug Complete ==="
echo "Check the generated debug files:"
ls -la debug_*.html 2>/dev/null || echo "No debug files yet"
