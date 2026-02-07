"""
Proper Adiga scraper based on actual site structure
"""
import time
import re
import requests
from typing import List, Dict, Any
from core.base_scraper import BaseScraper
from models.article import Article

class AdigaProperScraper(BaseScraper):
    def __init__(self, config: Dict[str, Any]):
        config['url'] = "https://www.adiga.kr"
        
        super().__init__(config)
        self.source_name = "adiga"
        
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        })
    
    def get_source_name(self) -> str:
        return self.source_name
    
    def fetch_articles(self) -> List[Dict[str, Any]]:
        """Fetch articles based on actual Adiga structure"""
        print("=== Adiga Proper Scraper ===")
        
        # Get main page
        main_url = f"{self.base_url}/man/inf/mainView.do?menuId=PCMANINF1000"
        print(f"DEBUG: Fetching main page: {main_url}")
        
        try:
            response = self.session.get(main_url, timeout=15)
            print(f"DEBUG: Status: {response.status_code}, Size: {len(response.content)} bytes")
            
            if response.status_code != 200:
                return []
            
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Save for debugging
            with open('adiga_main_analysis.html', 'w', encoding='utf-8') as f:
                f.write(response.text[:15000])
            
            # Strategy: Look for actual article links in the page
            articles = []
            
            # Find ALL links first
            all_links = soup.find_all('a')
            print(f"DEBUG: Total links on page: {len(all_links)}")
            
            # Look for article patterns
            article_patterns = [
                # Pattern 1: Links with prtlBbsId (article IDs)
                lambda href: 'prtlBbsId=' in href if href else False,
                
                # Pattern 2: Links to noticeDetail
                lambda href: 'noticeDetail.do' in href if href else False,
                
                # Pattern 3: Links that look like articles (not menu navigation)
                lambda href: href and 'menuId=' in href and 'Detail.do' in href,
            ]
            
            for link in all_links:
                try:
                    href = link.get('href', '')
                    text = link.get_text(strip=True)
                    
                    # Basic filtering
                    if not text or len(text) < 10:
                        continue
                    
                    # Skip navigation links
                    skip_terms = ['로그인', '회원가입', '검색', '사이트맵', '이전', '다음', '홈']
                    if any(term in text for term in skip_terms):
                        continue
                    
                    # Check if it matches article patterns
                    is_article_link = any(pattern(href) for pattern in article_patterns)
                    
                    # OR has admission keywords in text
                    admission_keywords = ['입학', '모집', '공고', '전형', '원서접수']
                    has_admission_keywords = any(keyword in text for keyword in admission_keywords)
                    
                    if is_article_link or has_admission_keywords:
                        # Build URL
                        url = self._build_url(href)
                        
                        # Get additional context
                        parent_text = ""
                        parent = link.parent
                        if parent:
                            parent_text = parent.get_text(strip=True, separator=' ')[:100]
                        
                        articles.append({
                            'title': text[:200],
                            'url': url,
                            'href': href,
                            'context': parent_text,
                            'is_article_link': is_article_link,
                            'has_admission_keywords': has_admission_keywords
                        })
                        
                        print(f"DEBUG: Potential article: {text[:60]}...")
                        print(f"       URL: {url[:80]}...")
                        
                except Exception as e:
                    continue
            
            # Filter for actual admission articles
            print(f"\nDEBUG: Found {len(articles)} potential articles, filtering...")
            
            filtered_articles = []
            for article in articles:
                title = article['title'].lower()
                url = article['url']
                
                # Filter criteria
                is_admission_related = any(keyword in title for keyword in [
                    '입학', '모집', '공고', '전형', '원서접수', '모집요강',
                    '정시', '수시', '추가모집', '정원'
                ])
                
                is_department_related = any(keyword in title for keyword in [
                    '음악', '영어', '한국어', '국어', '인문', '공학', '교육'
                ])
                
                has_year_pattern = re.search(r'\d{4}학년도', title)
                
                # Keep if it's clearly admission-related OR department-related with year
                if is_admission_related or (is_department_related and has_year_pattern):
                    filtered_articles.append(article)
                    print(f"DEBUG: ✓ Kept: {article['title'][:50]}...")
                else:
                    print(f"DEBUG: ✗ Filtered out: {article['title'][:50]}...")
            
            print(f"DEBUG: Final count: {len(filtered_articles)} admission articles")
            
            # If no articles found, use fallback strategy
            if not filtered_articles:
                print("DEBUG: No articles found, checking for any content...")
                
                # Look for any text that mentions admission
                all_text = soup.get_text()
                lines = [line.strip() for line in all_text.split('\n') if line.strip()]
                
                for line in lines:
                    if len(line) > 30:
                        for keyword in ['입학', '모집', '공고']:
                            if keyword in line:
                                filtered_articles.append({
                                    'title': line[:150],
                                    'url': main_url,
                                    'content': line,
                                    'is_fallback': True
                                })
                                print(f"DEBUG: Fallback found: {line[:80]}...")
                                break
                    
                    if len(filtered_articles) >= 3:
                        break
            
            return filtered_articles
            
        except Exception as e:
            print(f"DEBUG: Error: {e}")
            import traceback
            traceback.print_exc()
            return []
    
    def _build_url(self, href: str) -> str:
        """Build absolute URL"""
        if not href or href.startswith('javascript:'):
            return f"{self.base_url}/man/inf/mainView.do?menuId=PCMANINF1000"
        
        if href.startswith('http://') or href.startswith('https://'):
            return href
        
        if href.startswith('/'):
            return f"{self.base_url}{href}"
        
        return f"{self.base_url}/{href}"
    
    def parse_article(self, raw_data: Dict[str, Any]) -> Article:
        """Parse article content"""
        try:
            content = raw_data.get('content', '')
            
            # If fallback text, use it as content
            if content:
                return Article(
                    title=raw_data['title'],
                    url=raw_data['url'],
                    content=content,
                    source=self.source_name
                )
            
            # Try to fetch article content
            if raw_data['url'] and not raw_data['url'].endswith('menuId=PCMANINF1000'):
                try:
                    print(f"DEBUG: Fetching article: {raw_data['url']}")
                    response = self.session.get(raw_data['url'], timeout=10)
                    
                    if response.status_code == 200:
                        from bs4 import BeautifulSoup
                        soup = BeautifulSoup(response.content, 'html.parser')
                        
                        # Try to find article content
                        content_selectors = [
                            '.content', '.article-content', '.board-view',
                            '.view-content', 'article', 'main', '.bd', 'td.content'
                        ]
                        
                        for selector in content_selectors:
                            element = soup.select_one(selector)
                            if element:
                                content = element.get_text(strip=True, separator=' ')[:1000]
                                break
                        
                        if not content:
                            # Fallback: get body text
                            for tag in soup(['script', 'style']):
                                tag.decompose()
                            body = soup.find('body')
                            if body:
                                content = body.get_text(strip=True, separator=' ')[:800]
                except Exception as e:
                    print(f"DEBUG: Error fetching article: {e}")
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
                url=raw_data.get('url', f"{self.base_url}/man/inf/mainView.do?menuId=PCMANINF1000"),
                content="Parse error",
                source=self.source_name
            )

def test_proper_scraper():
    """Test the proper scraper"""
    print("=" * 60)
    print("ADIGA PROPER SCRAPER TEST")
    print("=" * 60)
    
    scraper = AdigaProperScraper({'url': 'https://adiga.kr'})
    articles = scraper.fetch_articles()
    
    print(f"\nResults: {len(articles)} articles found")
    
    for i, article in enumerate(articles[:10]):
        print(f"\n{i+1}. {article['title'][:80]}...")
        print(f"   URL: {article['url']}")
        if article.get('is_fallback'):
            print(f"   Type: Fallback text")
    
    # Test parsing if we have articles
    if articles:
        print("\n" + "=" * 60)
        print("ARTICLE PARSING TEST:")
        print("=" * 60)
        
        parsed = scraper.parse_article(articles[0])
        print(f"\nTitle: {parsed.title}")
        print(f"URL: {parsed.url}")
        print(f"Content length: {len(parsed.content)} chars")
        if parsed.content:
            print(f"Preview: {parsed.content[:200]}...")
    
    return articles

if __name__ == "__main__":
    test_proper_scraper()
