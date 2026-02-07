#!/bin/bash
echo "=== Comprehensive Adiga.kr Structure Analysis ==="

# First, let's explore the actual desktop site structure
echo "1. Exploring desktop site structure..."
DESKTOP_URL="https://www.adiga.kr/man/inf/mainView.do?menuId=PCMANINF1000"

# Get the main page and save it
curl -s "$DESKTOP_URL" -o adiga_desktop_full.html
echo "Desktop page size: $(wc -c < adiga_desktop_full.html) bytes"

# Extract all menu links
echo -e "\n2. Extracting all menu links..."
grep -o 'href="[^"]*"' adiga_desktop_full.html | grep -E "(menuId=|Article)" | head -30

# Look for specific admission-related menu items
echo -e "\n3. Searching for admission-related content..."
ADMISSION_KEYWORDS="입학|모집|공고|전형|원서|모집요강|정시|수시"

# Search in the HTML
echo "Keywords found in page:"
grep -n -i "$ADMISSION_KEYWORDS" adiga_desktop_full.html | head -20

# Look for menu structure
echo -e "\n4. Looking for menu/navigation structure..."
grep -n -i "nav\|menu\|gnb\|lnb" adiga_desktop_full.html | head -20

# Let's create a manual exploration script
echo -e "\n5. Creating manual exploration script..."
cat > explore_adiga.py << 'EXPLORE'
#!/usr/bin/env python3
"""
Manual exploration of Adiga.kr structure
"""
import requests
from bs4 import BeautifulSoup
import re

def explore_adiga():
    print("=== Manual Adiga.kr Exploration ===")
    
    base_url = "https://www.adiga.kr"
    desktop_url = f"{base_url}/man/inf/mainView.do?menuId=PCMANINF1000"
    
    # Create session
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    })
    
    # Get main page
    print(f"\n1. Fetching main desktop page: {desktop_url}")
    response = session.get(desktop_url)
    print(f"   Status: {response.status_code}, Size: {len(response.content)} bytes")
    
    soup = BeautifulSoup(response.content, 'html.parser')
    
    # Find all links
    all_links = soup.find_all('a')
    print(f"\n2. Total links found: {len(all_links)}")
    
    # Categorize links
    categories = {
        'menu_id_links': [],
        'article_links': [],
        'admission_links': [],
        'other_links': []
    }
    
    admission_keywords = ['입학', '모집', '공고', '전형', '원서', '모집요강']
    
    for link in all_links:
        href = link.get('href', '')
        text = link.get_text(strip=True)
        
        if not href:
            continue
        
        # Categorize
        if 'menuId=' in href:
            categories['menu_id_links'].append((text, href))
        elif 'Article' in href:
            categories['article_links'].append((text, href))
        elif any(keyword in text for keyword in admission_keywords):
            categories['admission_links'].append((text, href))
        elif text and len(text) > 3:
            categories['other_links'].append((text, href))
    
    # Print categories
    print("\n3. Link Categories:")
    print(f"   - Menu ID links: {len(categories['menu_id_links'])}")
    print(f"   - Article links: {len(categories['article_links'])}")
    print(f"   - Admission links: {len(categories['admission_links'])}")
    print(f"   - Other links: {len(categories['other_links'])}")
    
    # Show admission links
    if categories['admission_links']:
        print("\n4. Admission-related links found:")
        for text, href in categories['admission_links'][:10]:
            print(f"   - {text[:50]}... -> {href[:80]}")
    
    # Show menu ID links
    print("\n5. Menu ID links (first 20):")
    for i, (text, href) in enumerate(categories['menu_id_links'][:20]):
        print(f"   {i+1:2d}. {text[:40]:40} -> {href[:60]}")
    
    # Try to find announcement/notice sections
    print("\n6. Searching for announcement sections...")
    
    # Look for common announcement patterns
    announcement_patterns = [
        '공지사항', '새소식', '입학소식', '모집공고', 
        '학사공지', '대학소식', '입학안내', '공지'
    ]
    
    for pattern in announcement_patterns:
        elements = soup.find_all(string=re.compile(pattern, re.I))
        if elements:
            print(f"   Found '{pattern}' in {len(elements)} places")
            for elem in elements[:3]:
                parent = elem.parent
                print(f"     - Parent: {parent.name}, Text: {elem[:50]}...")
    
    # Look for board/list structures
    print("\n7. Looking for board/list structures...")
    
    board_classes = ['board', 'list', 'news', 'notice', 'bbs', 'article']
    for cls in board_classes:
        elements = soup.find_all(class_=re.compile(cls, re.I))
        if elements:
            print(f"   Found {len(elements)} elements with class containing '{cls}'")
    
    # Save the HTML for manual inspection
    with open('adiga_exploration.html', 'w', encoding='utf-8') as f:
        f.write(response.text[:10000])
    
    print(f"\n8. Saved exploration to 'adiga_exploration.html'")
    
    # Test some promising menu IDs
    print("\n9. Testing promising menu IDs...")
    
    promising_menus = [
        ('PCMANINF2000', '공지사항'),
        ('PCMANINF3000', '새소식'),
        ('PCUVTINF2000', '대학정보'),
        ('PCCLSINF2000', '학과정보'),
    ]
    
    for menu_id, description in promising_menus:
        test_url = f"{base_url}/man/inf/mainView.do?menuId={menu_id}"
        try:
            test_resp = session.get(test_url, timeout=10)
            print(f"   {menu_id} ({description}): {test_resp.status_code}, {len(test_resp.content)} bytes")
            
            # Check for admission content
            test_soup = BeautifulSoup(test_resp.content, 'html.parser')
            admission_count = len(test_soup.find_all(string=re.compile('|'.join(admission_keywords), re.I)))
            if admission_count > 0:
                print(f"     Found {admission_count} admission-related terms")
                
        except Exception as e:
            print(f"   {menu_id}: Error - {e}")
    
    return categories

if __name__ == "__main__":
    explore_adiga()
EXPLORE

chmod +x explore_adiga.py

echo -e "\n6. Running exploration..."
python3 explore_adiga.py

# Based on exploration, create the final targeted scraper
echo -e "\n7. Creating final targeted scraper based on exploration..."
cat > scrapers/adiga_targeted.py << 'TARGETED'
"""
Targeted Adiga scraper based on actual site structure exploration
"""
import time
import re
from typing import List, Dict, Any
from core.base_scraper import BaseScraper
from models.article import Article

class AdigaTargetedScraper(BaseScraper):
    def __init__(self, config: Dict[str, Any]):
        config['url'] = "https://www.adiga.kr"
        
        super().__init__(config)
        self.source_name = "adiga"
        
        # Based on exploration, these are promising menu IDs
        self.promising_menu_ids = [
            'PCMANINF2000',  # Likely 공지사항 (Notices)
            'PCMANINF3000',  # Likely 새소식 (News)
            'PCUVTINF2000',  # 대학정보 (University Info)
            'PCCLSINF2000',  # 학과정보 (Department Info)
        ]
        
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        })
    
    def get_source_name(self) -> str:
        return self.source_name
    
    def fetch_articles(self) -> List[Dict[str, Any]]:
        """Fetch from multiple promising menu IDs"""
        print("=== Adiga Targeted Scraper ===")
        
        all_articles = []
        
        for menu_id in self.promising_menu_ids:
            print(f"\nDEBUG: Checking menuId: {menu_id}")
            articles = self._fetch_from_menu(menu_id)
            all_articles.extend(articles)
            
            if articles:
                print(f"DEBUG: Found {len(articles)} articles from {menu_id}")
        
        # If no articles found, try the main page
        if not all_articles:
            print("DEBUG: No articles from menu IDs, trying main page...")
            main_articles = self._fetch_from_main()
            all_articles.extend(main_articles)
        
        # Filter for admission-related articles
        filtered_articles = self._filter_admission_articles(all_articles)
        print(f"\nDEBUG: Total after filtering: {len(filtered_articles)} admission articles")
        
        return filtered_articles
    
    def _fetch_from_menu(self, menu_id: str) -> List[Dict[str, Any]]:
        """Fetch articles from a specific menu ID"""
        try:
            url = f"{self.base_url}/man/inf/mainView.do?menuId={menu_id}"
            print(f"DEBUG: Fetching {url}")
            
            response = self.session.get(url, timeout=15)
            
            if response.status_code != 200:
                return []
            
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Look for article/list structures
            articles = []
            
            # Method 1: Look for list items
            list_items = soup.find_all(['li', 'tr'])
            print(f"DEBUG: Found {len(list_items)} list items/rows")
            
            for item in list_items[:50]:  # Check first 50
                try:
                    # Find links within list items
                    link = item.find('a')
                    if not link:
                        continue
                    
                    href = link.get('href', '')
                    text = link.get_text(strip=True)
                    
                    if not text or len(text) < 10:
                        continue
                    
                    # Skip navigation
                    if any(skip in text for skip in ['로그인', '회원가입', '검색', '더보기']):
                        continue
                    
                    # Build URL
                    url = self._build_url(href)
                    
                    # Get date if available
                    date_elem = item.find(['span', 'td', 'em', 'time'])
                    date = date_elem.get_text(strip=True) if date_elem else ""
                    
                    articles.append({
                        'title': text[:200],
                        'url': url,
                        'date': date,
                        'menu_id': menu_id,
                        'raw_href': href
                    })
                    
                except:
                    continue
            
            # Method 2: Look for board/list containers
            if len(articles) < 5:
                board_selectors = ['.board', '.list', '.news', '.bbs', 'table']
                for selector in board_selectors:
                    boards = soup.select(selector)
                    if boards:
                        print(f"DEBUG: Found {len(boards)} elements with selector '{selector}'")
                        # Extract from first board
                        board_articles = self._extract_from_board(boards[0])
                        articles.extend(board_articles)
                        break
            
            return articles
            
        except Exception as e:
            print(f"DEBUG: Error fetching menu {menu_id}: {e}")
            return []
    
    def _fetch_from_main(self) -> List[Dict[str, Any]]:
        """Fetch from main page as fallback"""
        try:
            url = f"{self.base_url}/man/inf/mainView.do?menuId=PCMANINF1000"
            response = self.session.get(url, timeout=15)
            
            if response.status_code != 200:
                return []
            
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Look for news/announcement sections
            articles = []
            
            # Common section titles
            section_titles = ['공지사항', '새소식', '입학소식', '모집공고']
            
            for title in section_titles:
                elements = soup.find_all(string=re.compile(title, re.I))
                for element in elements:
                    # Get the section container
                    section = element.find_parent(['div', 'section', 'ul', 'table'])
                    if section:
                        section_articles = self._extract_from_section(section)
                        articles.extend(section_articles)
                        print(f"DEBUG: Found section '{title}' with {len(section_articles)} articles")
            
            return articles
            
        except Exception as e:
            print(f"DEBUG: Error fetching main: {e}")
            return []
    
    def _extract_from_board(self, board) -> List[Dict[str, Any]]:
        """Extract articles from a board/table element"""
        articles = []
        
        try:
            # Find all rows or list items
            rows = board.find_all(['tr', 'li'])
            
            for row in rows[:30]:  # Check first 30
                try:
                    link = row.find('a')
                    if not link:
                        continue
                    
                    href = link.get('href', '')
                    text = link.get_text(strip=True)
                    
                    if not text or len(text) < 10:
                        continue
                    
                    url = self._build_url(href)
                    
                    articles.append({
                        'title': text[:200],
                        'url': url,
                        'raw_href': href
                    })
                    
                except:
                    continue
                    
        except:
            pass
        
        return articles
    
    def _extract_from_section(self, section) -> List[Dict[str, Any]]:
        """Extract articles from a section"""
        articles = []
        
        try:
            links = section.find_all('a')
            
            for link in links[:20]:  # Check first 20
                try:
                    href = link.get('href', '')
                    text = link.get_text(strip=True)
                    
                    if not text or len(text) < 10:
                        continue
                    
                    url = self._build_url(href)
                    
                    articles.append({
                        'title': text[:200],
                        'url': url,
                        'raw_href': href
                    })
                    
                except:
                    continue
                    
        except:
            pass
        
        return articles
    
    def _filter_admission_articles(self, articles: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Filter for admission-related articles only"""
        admission_keywords = [
            '입학', '모집', '공고', '전형', '원서접수', '모집요강',
            '정시', '수시', '추가모집', '정원', '면접', '실기시험'
        ]
        
        department_keywords = [
            '음악', '영어', '한국어', '국어', '인문', '공학', '교육',
            '성악', '작곡', '영문', '국문', '인문학', '교양'
        ]
        
        filtered = []
        
        for article in articles:
            title = article.get('title', '').lower()
            
            # Check if it's admission-related
            is_admission = any(keyword in title for keyword in admission_keywords)
            
            # OR if it mentions specific departments
            is_dept_related = any(keyword in title for keyword in department_keywords)
            
            # Also check for year patterns (2026학년도, 2027학년도)
            has_year = re.search(r'\d{4}학년도', title)
            
            if is_admission or (is_dept_related and has_year):
                filtered.append(article)
        
        return filtered
    
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
            content = ""
            
            if raw_data['url'] and not raw_data['url'].endswith('menuId=PCMANINF1000'):
                try:
                    print(f"DEBUG: Fetching article: {raw_data['url']}")
                    response = self.session.get(raw_data['url'], timeout=10)
                    
                    if response.status_code == 200:
                        from bs4 import BeautifulSoup
                        soup = BeautifulSoup(response.content, 'html.parser')
                        
                        # Try different content selectors
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

def test_targeted_scraper():
    """Test the targeted scraper"""
    print("=" * 60)
    print("ADIGA TARGETED SCRAPER TEST")
    print("=" * 60)
    
    scraper = AdigaTargetedScraper({'url': 'https://adiga.kr'})
    articles = scraper.fetch_articles()
    
    print(f"\nResults: {len(articles)} admission-related articles found")
    
    for i, article in enumerate(articles[:10]):
        print(f"\n{i+1}. {article['title'][:80]}...")
        print(f"   URL: {article['url']}")
        if article.get('menu_id'):
            print(f"   Menu ID: {article['menu_id']}")
    
    return articles

if __name__ == "__main__":
    test_targeted_scraper()
TARGETED

echo -e "\n8. Testing targeted scraper..."
python3 -c "
import sys
sys.path.insert(0, '.')
try:
    from scrapers.adiga_targeted import test_targeted_scraper
    articles = test_targeted_scraper()
    
    if articles:
        print('\\n✅ TARGETED SCRAPER WORKING! Found admission articles.')
        print('\\nTo integrate:')
        print('  cp scrapers/adiga_targeted.py scrapers/adiga_scraper.py')
        print('  sed -i \\'s/class AdigaTargetedScraper/class AdigaScraper/\\' scrapers/adiga_scraper.py')
    else:
        print('\\n⚠ No admission articles found.')
        print('We may need to:')
        print('1. Check if there are current admission announcements')
        print('2. Try different menu IDs')
        print('3. Adjust filtering criteria')
        
except Exception as e:
    print(f'\\n❌ Error: {e}')
    import traceback
    traceback.print_exc()
"

echo -e "\n=== Analysis Complete ==="
echo "Next steps:"
echo "1. Run the exploration script to understand Adiga structure"
echo "2. Test the targeted scraper"
echo "3. If no articles found, we may need to:"
echo "   - Check different menu IDs"
echo "   - Wait for actual admission season"
echo "   - Use mock data for testing until real data available"
echo ""
echo "Generated files:"
echo "  - adiga_desktop_full.html (full desktop page)"
echo "  - adiga_exploration.html (structured exploration)"
