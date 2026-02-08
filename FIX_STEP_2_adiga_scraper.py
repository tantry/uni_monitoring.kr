#!/usr/bin/env python3
"""
ROBUST ADIGA SCRAPER - FIXED VERSION

Key changes from the broken version:
1. Fetches from /cct/pbf/noticeList.do (actual notice board) instead of /man/inf/ (container)
2. Looks for links with prtlBbsId parameter (actual articles)
3. Implements content quality validation
4. Rejects navigation/empty content
5. Only sends real announcements to Telegram
"""

import logging
import re
import requests
from typing import List, Dict, Any, Optional
from datetime import datetime

try:
    from core.base_scraper import BaseScraper
    from models.article import Article
except ImportError:
    # Fallback for testing
    class BaseScraper:
        def __init__(self, config):
            self.config = config
            self.base_url = config.get('url', 'https://www.adiga.kr')
            self.session = requests.Session()
    
    class Article:
        def __init__(self, **kwargs):
            self.__dict__.update(kwargs)

logger = logging.getLogger(__name__)

class AdigaScraper(BaseScraper):
    """
    Adiga.kr scraper that correctly identifies and extracts actual admission announcements.
    """
    
    def __init__(self, config: Dict[str, Any]):
        if 'url' not in config:
            config['url'] = "https://www.adiga.kr"
        
        super().__init__(config)
        self.source_name = "adiga"
        
        # Configuration for announcement boards
        self.announcement_boards = [
            {
                'name': '공지사항',
                'path': '/cct/pbf/noticeList.do',
                'menu_id': 'PCCCTPBF1000',
                'enabled': True
            },
            {
                'name': '대입주요자료',
                'path': '/uct/nmg/enw/newsView.do',
                'menu_id': 'PCUCTNMG2000',
                'enabled': True
            }
        ]
        
        # Quality rules for filtering
        self.quality_rules = {
            'min_content_length': 50,
            'reject_patterns': ['바로가기', '퀵메뉴', '메뉴'], 
            'accept_keywords': ['모집', '공고', '입학', '입시', '전형']
        }
        
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        })
    
    def get_source_name(self) -> str:
        return self.source_name
    
    def fetch_articles(self) -> List[Dict[str, Any]]:
        """
        Fetch articles from the actual announcement boards.
        
        Returns:
            List of articles with title, url, content, etc.
        """
        print("\n" + "="*80)
        print(f"ADIGA ROBUST SCRAPER v2 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*80)
        
        all_articles = []
        
        # Try each announcement board
        for board in self.announcement_boards:
            if not board['enabled']:
                continue
            
            print(f"\n📋 Fetching from: {board['name']}")
            print(f"   Path: {board['path']}")
            print(f"   Menu ID: {board['menu_id']}")
            
            try:
                articles = self._fetch_from_board(board)
                print(f"   ✓ Found {len(articles)} articles")
                all_articles.extend(articles)
                
            except Exception as e:
                print(f"   ✗ Error: {str(e)[:100]}")
                logger.error(f"Error fetching from {board['name']}: {e}")
        
        # Apply quality filtering
        print(f"\n🔍 Applying quality filters...")
        filtered = self._apply_quality_filters(all_articles)
        
        print(f"\n{'='*80}")
        print(f"RESULT: {len(all_articles)} articles found → {len(filtered)} high-quality")
        print(f"{'='*80}\n")
        
        return filtered
    
    def _fetch_from_board(self, board: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Fetch articles from a specific announcement board.
        """
        articles = []
        
        try:
            # Build URL to the announcement list
            url = f"{self.base_url}{board['path']}"
            if board.get('menu_id'):
                url += f"?menuId={board['menu_id']}"
            
            print(f"   GET: {url}")
            
            response = self.session.get(url, timeout=15)
            print(f"   Status: {response.status_code}, Size: {len(response.content)} bytes")
            
            if response.status_code != 200:
                logger.warning(f"Status {response.status_code} for {url}")
                return articles
            
            # Parse HTML
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Strategy 1: Look for links with prtlBbsId (actual article IDs)
            print(f"   → Searching for article links (prtlBbsId)...")
            
            article_links = soup.find_all('a', href=re.compile(r'prtlBbsId=\d+'))
            print(f"     Found {len(article_links)} potential articles")
            
            for link in article_links[:50]:  # Limit to first 50
                try:
                    title = link.get_text(strip=True)
                    href = link.get('href', '')
                    
                    # Skip if no title or too short
                    if not title or len(title) < 5:
                        continue
                    
                    # Build absolute URL
                    if href.startswith('http'):
                        full_url = href
                    elif href.startswith('/'):
                        full_url = f"{self.base_url}{href}"
                    else:
                        full_url = f"{self.base_url}/{href}"
                    
                    # Extract date if available (usually in next td)
                    date_text = ""
                    parent_row = link.find_parent(['tr', 'li', 'div'])
                    if parent_row:
                        date_elem = parent_row.find(['td', 'span', 'em'])
                        if date_elem:
                            date_text = date_elem.get_text(strip=True)
                    
                    articles.append({
                        'title': title[:300],
                        'url': full_url,
                        'board': board['name'],
                        'date': date_text,
                        'source': self.source_name,
                        'content': '',  # Will be fetched during parsing
                        'fetched_at': datetime.now().isoformat(),
                    })
                    
                except Exception as e:
                    logger.debug(f"Error extracting article: {e}")
                    continue
            
            # Strategy 2: If few articles found, try table/list rows
            if len(articles) < 5:
                print(f"   → Searching table/list rows...")
                
                rows = soup.find_all(['tr', 'li'], limit=50)
                for row in rows:
                    try:
                        # Skip header rows
                        if row.find(['th', 'thead']):
                            continue
                        
                        # Look for links in this row
                        link = row.find('a')
                        if not link:
                            continue
                        
                        text = link.get_text(strip=True)
                        if len(text) > 5:
                            href = link.get('href', '')
                            
                            if not any(skip in text for skip in ['로그인', '회원가입', '검색']):
                                if href.startswith('http'):
                                    url = href
                                else:
                                    url = f"{self.base_url}{href}" if href.startswith('/') else f"{self.base_url}/{href}"
                                
                                articles.append({
                                    'title': text[:300],
                                    'url': url,
                                    'board': board['name'],
                                    'date': '',
                                    'source': self.source_name,
                                    'content': '',
                                    'fetched_at': datetime.now().isoformat(),
                                })
                    except:
                        continue
        
        except Exception as e:
            logger.error(f"Error fetching board {board['name']}: {e}")
            import traceback
            traceback.print_exc()
        
        return articles
    
    def _apply_quality_filters(self, articles: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Filter articles to remove low-value content.
        """
        filtered = []
        rejected_reasons = {
            'empty_content': 0,
            'navigation_text': 0,
            'no_keywords': 0,
            'other': 0
        }
        
        for article in articles:
            reason = None
            
            # Check 1: Does title have admission keywords?
            title_lower = article['title'].lower()
            has_keyword = any(
                kw in title_lower 
                for kw in self.quality_rules['accept_keywords']
            )
            
            if not has_keyword:
                reason = 'no_keywords'
            
            # Check 2: Does title contain rejection patterns?
            if not reason:
                is_navigation = any(
                    pattern in title_lower 
                    for pattern in self.quality_rules['reject_patterns']
                )
                
                if is_navigation:
                    reason = 'navigation_text'
            
            # Check 3: Content length (after fetching)
            # This will be checked during parse_article
            
            if not reason:
                filtered.append(article)
            else:
                rejected_reasons[reason] = rejected_reasons.get(reason, 0) + 1
        
        # Log filtering results
        print(f"   Articles rejected:")
        for reason, count in rejected_reasons.items():
            if count > 0:
                print(f"     - {reason}: {count}")
        
        return filtered
    
    def parse_article(self, raw_data: Dict[str, Any]) -> Article:
        """
        Parse raw article data and fetch full content.
        
        Args:
            raw_data: Raw article from fetch_articles()
            
        Returns:
            Article object with parsed content
        """
        try:
            title = raw_data.get('title', '')
            url = raw_data.get('url', '')
            content = ""
            
            # Try to fetch article content
            if url and not url.endswith('mainView.do'):
                try:
                    print(f"   Fetching: {title[:50]}...")
                    response = self.session.get(url, timeout=10)
                    
                    if response.status_code == 200:
                        from bs4 import BeautifulSoup
                        soup = BeautifulSoup(response.content, 'html.parser')
                        
                        # Try multiple content selectors
                        content_selectors = [
                            '.board-view',
                            '.article-content', 
                            '.content',
                            '.view-content',
                            'article',
                            'main',
                            '.bd'
                        ]
                        
                        for selector in content_selectors:
                            element = soup.select_one(selector)
                            if element:
                                content = element.get_text(strip=True, separator=' ')[:1000]
                                break
                        
                        # Fallback: get body text
                        if not content:
                            for tag in soup(['script', 'style', 'nav']):
                                tag.decompose()
                            body = soup.find('body')
                            if body:
                                content = body.get_text(strip=True, separator=' ')[:800]
                
                except Exception as e:
                    logger.debug(f"Error fetching content: {e}")
                    content = ""
            
            # Quality check: reject if content is too short or just navigation
            if content:
                # Check for navigation text
                nav_patterns = ['바로가기', '퀵메뉴', '메뉴바로가기']
                if any(pattern in content for pattern in nav_patterns):
                    content = ""
                
                # Check minimum length
                if len(content) < self.quality_rules['min_content_length']:
                    content = ""
            
            # Detect department
            department = self.detect_department(raw_data)
            
            # Create Article object
            article = Article(
                title=title,
                url=url,
                content=content,
                source=raw_data.get('source', self.source_name),
                published_date=raw_data.get('date', ''),
                department=department,
                board=raw_data.get('board', ''),
                content_quality='high' if content else 'low',
                content_length=len(content)
            )
            
            return article
            
        except Exception as e:
            logger.error(f"Error parsing article: {e}")
            
            return Article(
                title=raw_data.get('title', 'Parse Error'),
                url=raw_data.get('url', ''),
                content=f"Error: {str(e)[:100]}",
                source=self.source_name,
                department=None,
                content_quality='error'
            )
    
    def detect_department(self, article_data: Dict[str, Any]) -> Optional[str]:
        """
        Detect which department this article is about.
        """
        text = f"{article_data.get('title', '')} {article_data.get('board', '')}"
        text_lower = text.lower()
        
        # Department keyword mapping
        departments = {
            'music': ['음악', '성악', '작곡', '실용음악'],
            'korean': ['한국어', '국어', '국문'],
            'english': ['영어', '영문'],
            'liberal': ['인문', '교양'],
        }
        
        for dept_name, keywords in departments.items():
            if any(keyword in text_lower for keyword in keywords):
                return dept_name
        
        return None


# Test function
if __name__ == "__main__":
    import sys
    
    print("\n🧪 Testing AdigaScraper...")
    
    scraper = AdigaScraper({'url': 'https://www.adiga.kr'})
    
    # Fetch articles
    articles = scraper.fetch_articles()
    
    print(f"\n📊 RESULTS: {len(articles)} articles\n")
    
    if articles:
        # Show summary
        for i, article in enumerate(articles[:5], 1):
            print(f"{i}. {article.get('title', 'NO TITLE')[:70]}")
            print(f"   Board: {article.get('board', 'unknown')}")
            if article.get('date'):
                print(f"   Date: {article['date']}")
            print(f"   URL: {article.get('url', 'NO URL')[:80]}\n")
        
        # Parse first article for detailed view
        if articles:
            print("\n" + "="*80)
            print("PARSING FIRST ARTICLE FOR FULL CONTENT")
            print("="*80)
            
            parsed = scraper.parse_article(articles[0])
            
            print(f"\nTitle: {parsed.title}")
            print(f"Department: {parsed.department}")
            print(f"Content length: {len(parsed.content)} chars")
            print(f"Content quality: {parsed.content_quality}")
            
            if parsed.content:
                print(f"\nContent preview:")
                print(f"{parsed.content[:300]}...")
            else:
                print(f"\n⚠ No content extracted")
    else:
        print("⚠ No articles found")
        print("\nThis could mean:")
        print("1. Adiga changed their URL structure")
        print("2. No announcements during off-season")
        print("3. Need to add more board URLs")
