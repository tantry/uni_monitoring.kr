#!/bin/bash
echo "=== Finding REAL Admission Articles ==="

# Check the saved HTML for actual article patterns
echo "1. Searching for prtlBbsId (article IDs)..."
grep -n "prtlBbsId=" adiga_desktop_full.html | head -20

echo -e "\n2. Searching for noticeDetail (article detail pages)..."
grep -n "noticeDetail" adiga_desktop_full.html | head -10

echo -e "\n3. Looking for actual article titles with admission keywords..."
ADMISSION_KEYWORDS="입학|모집|공고|전형|원서|모집요강|정시|수시"
grep -B2 -A2 "$ADMISSION_KEYWORDS" adiga_desktop_full.html | grep -v "menuId=" | head -30

echo -e "\n4. Creating the correct scraper..."
cat > scrapers/adiga_article_focused.py << 'ARTICLEFOCUSED'
"""
Adiga scraper focused on ACTUAL articles not navigation links
"""
import time
import re
from typing import List, Dict, Any
from core.base_scraper import BaseScraper
from models.article import Article

class AdigaArticleFocusedScraper(BaseScraper):
    def __init__(self, config: Dict[str, Any]):
        config['url'] = "https://www.adiga.kr"
        
        super().__init__(config)
        self.source_name = "adiga"
        
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        })
    
    def get_source_name(self) -> str:
        return self.source_name
    
    def fetch_articles(self) -> List[Dict[str, Any]]:
        """Fetch ACTUAL articles, not navigation links"""
        print("=== Adiga Article-Focused Scraper ===")
        
        # First, get the 공지사항 (notice board) page
        notice_url = f"{self.base_url}/cct/pbf/noticeList.do?menuId=PCCCTPBF1000"
        print(f"DEBUG: Fetching notice board: {notice_url}")
        
        try:
            response = self.session.get(notice_url, timeout=15)
            print(f"DEBUG: Status: {response.status_code}, Size: {len(response.content)} bytes")
            
            if response.status_code != 200:
                print(f"DEBUG: Failed to get notice board")
                return []
            
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Save for analysis
            with open('notice_board_content.html', 'w', encoding='utf-8') as f:
                f.write(response.text[:10000])
            
            # Strategy 1: Look for actual article links with prtlBbsId
            articles = []
            
            print("DEBUG: Searching for article links with prtlBbsId...")
            
            # Find all links that contain prtlBbsId (article IDs)
            all_links = soup.find_all('a', href=re.compile(r'prtlBbsId=\d+'))
            print(f"DEBUG: Found {len(all_links)} links with prtlBbsId")
            
            for link in all_links[:20]:  # Check first 20
                try:
                    href = link.get('href', '')
                    text = link.get_text(strip=True)
                    
                    # Skip if no meaningful text
                    if not text or len(text) < 10:
                        continue
                    
                    # Skip common non-article text
                    if any(skip in text for skip in ['이전', '다음', '처음', '끝', '목록']):
                        continue
                    
                    # Build URL
                    if href.startswith('/'):
                        url = f"{self.base_url}{href}"
                    elif href.startswith('http'):
                        url = href
                    else:
                        url = f"{self.base_url}/{href}"
                    
                    articles.append({
                        'title': text[:200],
                        'url': url,
                        'href': href,
                        'type': 'prtlBbsId'
                    })
                    
                    print(f"DEBUG: Found article: {text[:60]}...")
                    
                except Exception as e:
                    print(f"DEBUG: Error processing link: {e}")
                    continue
            
            # Strategy 2: Look for table rows in notice board (common pattern)
            if len(articles) < 5:
                print("DEBUG: Searching for table rows...")
                
                tables = soup.find_all('table')
                for table in tables[:3]:  # Check first 3 tables
                    rows = table.find_all('tr')
                    print(f"DEBUG: Table has {len(rows)} rows")
                    
                    for row in rows:
                        # Look for links in table rows that look like articles
                        links = row.find_all('a')
                        for link in links:
                            try:
                                href = link.get('href', '')
                                text = link.get_text(strip=True)
                                
                                # Article-like text (not too short, not navigation)
                                if text and 15 <= len(text) <= 200:
                                    # Check for admission keywords
                                    admission_keywords = ['입학', '모집', '공고', '전형']
                                    if any(keyword in text for keyword in admission_keywords):
                                        # Build URL
                                        if href and not href.startswith('javascript:'):
                                            if href.startswith('/'):
                                                url = f"{self.base_url}{href}"
                                            elif href.startswith('http'):
                                                url = href
                                            else:
                                                url = f"{self.base_url}/{href}"
                                        else:
                                            continue
                                        
                                        # Check if we already have this URL
                                        if any(a['url'] == url for a in articles):
                                            continue
                                        
                                        articles.append({
                                            'title': text[:200],
                                            'url': url,
                                            'href': href,
                                            'type': 'table_row'
                                        })
                                        
                                        print(f"DEBUG: Found in table: {text[:60]}...")
                                        
                            except:
                                continue
            
            # Strategy 3: If still no articles, try the main page for announcements
            if not articles:
                print("DEBUG: Trying main page for announcements...")
                main_url = f"{self.base_url}/man/inf/mainView.do?menuId=PCMANINF1000"
                main_response = self.session.get(main_url, timeout=15)
                
                if main_response.status_code == 200:
                    main_soup = BeautifulSoup(main_response.content, 'html.parser')
                    
                    # Look for announcement sections
                    announcement_keywords = ['공지사항', '새소식', '알림', '안내']
                    for keyword in announcement_keywords:
                        elements = main_soup.find_all(string=re.compile(keyword, re.I))
                        for element in elements:
                            # Find the container
                            container = element.find_parent(['div', 'section', 'ul'])
                            if container:
                                container_links = container.find_all('a')
                                for link in container_links[:10]:
                                    try:
                                        href = link.get('href', '')
                                        text = link.get_text(strip=True)
                                        
                                        if text and len(text) >= 10:
                                            # Build URL
                                            if href and not href.startswith('javascript:'):
                                                if href.startswith('/'):
                                                    url = f"{self.base_url}{href}"
                                                elif href.startswith('http'):
                                                    url = href
                                                else:
                                                    url = f"{self.base_url}/{href}"
                                            else:
                                                continue
                                            
                                            articles.append({
                                                'title': text[:200],
                                                'url': url,
                                                'href': href,
                                                'type': 'announcement'
                                            })
                                            
                                            print(f"DEBUG: Found announcement: {text[:60]}...")
                                            
                                    except:
                                        continue
            
            # Filter for admission-related articles
            print(f"DEBUG: Found {len(articles)} total links, filtering for admission...")
            
            admission_articles = []
            admission_keywords = [
                '입학', '모집', '공고', '전형', '원서접수', '모집요강',
                '정시', '수시', '추가모집', '정원', '면접', '실기'
            ]
            
            for article in articles:
                title = article['title'].lower()
                
                # Check if it's admission-related
                is_admission = any(keyword in title for keyword in admission_keywords)
                
                # Also check for university/department patterns
                dept_keywords = ['음악', '영어', '한국어', '국어', '인문', '공학', '교육']
                is_dept_related = any(keyword in title for keyword in dept_keywords)
                
                # Check for year patterns (2026학년도, 2027학년도)
                has_year = re.search(r'\d{4}학년도', title)
                
                if is_admission or (is_dept_related and has_year):
                    admission_articles.append(article)
                    print(f"DEBUG: Kept as admission: {article['title'][:50]}...")
                else:
                    print(f"DEBUG: Filtered out: {article['title'][:50]}...")
            
            print(f"DEBUG: Final count: {len(admission_articles)} admission articles")
            return admission_articles
            
        except Exception as e:
            print(f"DEBUG: Error: {e}")
            import traceback
            traceback.print_exc()
            return []
    
    def parse_article(self, raw_data: Dict[str, Any]) -> Article:
        """Parse article content"""
        try:
            content = ""
            
            if raw_data['url']:
                try:
                    print(f"DEBUG: Fetching article content: {raw_data['url']}")
                    response = self.session.get(raw_data['url'], timeout=10)
                    
                    if response.status_code == 200:
                        from bs4 import BeautifulSoup
                        soup = BeautifulSoup(response.content, 'html.parser')
                        
                        # Try to find article content
                        content_selectors = [
                            '.content', '.article-content', '.board-view',
                            '.view-content', 'article', 'main', '.bd'
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
                    print(f"DEBUG: Error fetching article content: {e}")
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

def test_article_focused():
    """Test the article-focused scraper"""
    print("=" * 60)
    print("ADIGA ARTICLE-FOCUSED SCRAPER TEST")
    print("=" * 60)
    
    scraper = AdigaArticleFocusedScraper({'url': 'https://adiga.kr'})
    articles = scraper.fetch_articles()
    
    print(f"\nResults: {len(articles)} admission articles found")
    
    for i, article in enumerate(articles[:10]):
        print(f"\n{i+1}. {article['title'][:80]}...")
        print(f"   URL: {article['url']}")
        print(f"   Type: {article.get('type', 'unknown')}")
    
    return articles

if __name__ == "__main__":
    test_article_focused()
ARTICLEFOCUSED

# Test the new scraper
echo -e "\n5. Testing article-focused scraper..."
python3 -c "
import sys
sys.path.insert(0, '.')
try:
    from scrapers.adiga_article_focused import test_article_focused
    articles = test_article_focused()
    
    if articles:
        print('\\n✅ ARTICLE-FOCUSED SCRAPER WORKING! Found actual articles.')
        print('\\nTo integrate:')
        print('  cp scrapers/adiga_article_focused.py scrapers/adiga_scraper.py')
        print('  sed -i \\'s/class AdigaArticleFocusedScraper/class AdigaScraper/\\' scrapers/adiga_scraper.py')
    else:
        print('\\n⚠ No admission articles found.')
        print('This might mean:')
        print('1. No current admission announcements on Adiga')
        print('2. Need to check different notice boards')
        print('3. Site structure may have changed')
        
except Exception as e:
    print(f'\\n❌ Error: {e}')
    import traceback
    traceback.print_exc()
"

echo -e "\n=== Fix Complete ==="
echo "The new scraper specifically targets:"
echo "1. Notice board at /cct/pbf/noticeList.do?menuId=PCCCTPBF1000"
echo "2. Articles with prtlBbsId (article IDs)"
echo "3. Actual admission announcements, not navigation links"
