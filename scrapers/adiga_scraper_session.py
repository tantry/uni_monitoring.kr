#!/usr/bin/env python3
"""
Adiga.kr Scraper with Session Support - FIXES 404 LINKS
Based on working implementation from uni_monitor.py
"""
import re
import requests
from typing import List, Dict, Any, Optional
from bs4 import BeautifulSoup
from datetime import datetime
import os
import sys
import time

# Add the parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.base_scraper import BaseScraper


class AdigaScraper(BaseScraper):
    """Adiga.kr scraper with proper session handling for working links."""
    
    def __init__(self, config: Dict[str, Any] = None):
        """
        Initialize with session support.
        """
        if config is None:
            config = {
                'name': 'adiga',
                'base_url': 'https://adiga.kr',
                'html_file_path': 'adiga_structure.html',
                'max_articles': 10,
                'display_name': 'Adiga Session (어디가)',
                'timeout': 30,
                'retry_attempts': 3
            }
        
        base_config = {
            'name': config.get('name', 'adiga'),
            'base_url': config.get('base_url', 'https://adiga.kr'),
            'timeout': config.get('timeout', 30),
            'retry_attempts': config.get('retry_attempts', 3)
        }
        
        super().__init__(base_config)
        
        self.full_config = config
        self.html_file_path = config.get('html_file_path', 'adiga_structure.html')
        self.max_articles = config.get('max_articles', 10)
        self.display_name = config.get('display_name', 'Adiga Session (어디가)')
        
        # Initialize session (will be created on first use)
        self._session = None
        
        # Backward compatibility
        self.source_config = {
            'name': self.display_name,
            'base_url': self.base_url,
            'type': 'university_admission_session'
        }
        self.source_name = self.display_name
        
        self.logger.info(f"Initialized {self.display_name} scraper with session support")
    
    @property
    def session(self):
        """Lazy initialization of session"""
        if self._session is None:
            self._session = requests.Session()
            # Set proper headers to mimic browser
            self._session.headers.update({
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7',
                'Accept-Encoding': 'gzip, deflate, br',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
                'Referer': 'https://adiga.kr/',
            })
            self.logger.debug("Created new requests session")
        return self._session
    
    def fetch_articles(self) -> List[Dict[str, Any]]:
        """
        Fetch articles with session support.
        """
        self.logger.info(f"Fetching articles with session support")
        
        raw_articles = []
        
        try:
            # METHOD 1: Try live HTTP scraping with session
            self.logger.info("Attempting live HTTP scrape with session...")
            live_articles = self._fetch_live_articles()
            
            if live_articles:
                raw_articles = live_articles
                self.logger.info(f"Live scrape successful: {len(raw_articles)} articles")
            else:
                # METHOD 2: Fallback to local HTML file
                self.logger.info("Falling back to local HTML file...")
                raw_articles = self._parse_local_html()
                
        except Exception as e:
            self.logger.error(f"Fetch error: {e}")
            raw_articles = self._get_fallback_articles()
        
        # Enhance articles with session info
        enhanced_articles = []
        for article in raw_articles:
            enhanced = self._enhance_with_session_info(article)
            enhanced_articles.append(enhanced)
        
        return enhanced_articles
    
    def _fetch_live_articles(self) -> List[Dict[str, Any]]:
        """Fetch articles directly from Adiga.kr with session"""
        try:
            # Step 1: Visit main page to establish session
            self.logger.info("Establishing session with adiga.kr...")
            main_response = self.session.get(
                self.base_url,
                timeout=self.timeout,
                allow_redirects=True
            )
            
            if main_response.status_code != 200:
                self.logger.warning(f"Main page returned {main_response.status_code}")
                return []
            
            self.logger.info(f"Session established. Cookies: {len(self.session.cookies)}")
            
            # Step 2: Try to get article list
            # Adiga might use different endpoints - try common ones
            endpoints = [
                f"{self.base_url}/ArticleList.do",
                f"{self.base_url}/BoardList.do",
                f"{self.base_url}/List.do",
                self.base_url  # Main page might have articles
            ]
            
            for endpoint in endpoints:
                try:
                    self.logger.info(f"Trying endpoint: {endpoint}")
                    response = self.session.get(
                        endpoint,
                        timeout=self.timeout,
                        allow_redirects=True
                    )
                    
                    if response.status_code == 200:
                        return self._parse_html_response(response.text, live=True)
                    
                except requests.exceptions.RequestException as e:
                    self.logger.warning(f"Endpoint {endpoint} failed: {e}")
                    continue
            
            return []
            
        except Exception as e:
            self.logger.error(f"Live fetch error: {e}")
            return []
    
    def _parse_local_html(self) -> List[Dict[str, Any]]:
        """Parse local HTML file"""
        raw_articles = []
        
        if not os.path.exists(self.html_file_path):
            self.logger.error(f"Local HTML file not found: {self.html_file_path}")
            return self._get_fallback_articles()
        
        try:
            with open(self.html_file_path, 'r', encoding='utf-8') as f:
                html = f.read()
            
            return self._parse_html_response(html, live=False)
            
        except Exception as e:
            self.logger.error(f"Error parsing local HTML: {e}")
            return self._get_fallback_articles()
    
    def _parse_html_response(self, html: str, live: bool) -> List[Dict[str, Any]]:
        """Parse HTML response (live or local)"""
        soup = BeautifulSoup(html, 'html.parser')
        raw_articles = []
        
        # Look for article items
        article_items = soup.select('ul.uctList02 li')
        
        if not article_items:
            # Try alternative selectors
            selectors = ['.article-item', '.list-item', 'tr[onclick*="fnDetailPopup"]']
            for selector in selectors:
                items = soup.select(selector)
                if items:
                    article_items = items
                    break
        
        self.logger.info(f"Found {len(article_items)} article items (live={live})")
        
        for item in article_items[:self.max_articles]:
            try:
                article = self._extract_article(item, live)
                if article:
                    raw_articles.append(article)
            except Exception as e:
                self.logger.debug(f"Failed to parse item: {e}")
                continue
        
        return raw_articles
    
    def _extract_article(self, item, live: bool) -> Optional[Dict[str, Any]]:
        """Extract article data from item"""
        # Find clickable element with fnDetailPopup
        clickable = None
        for elem in item.find_all(True, onclick=True):  # True = all tags
            onclick = elem.get('onclick', '')
            if 'fnDetailPopup' in onclick:
                clickable = elem
                break
        
        if not clickable:
            return None
        
        onclick = clickable.get('onclick', '')
        match = re.search(r'fnDetailPopup\(["\'](\d+)["\']\)', onclick)
        if not match:
            return None
        
        article_id = match.group(1)
        
        # Extract title
        title = ""
        title_elem = item.select_one('.uctCastTitle')
        if title_elem:
            title = title_elem.get_text(strip=True).replace('newIcon', '').strip()
        
        if not title:
            # Fallback: get text from first 100 chars
            title = item.get_text(strip=True)[:100]
        
        # Extract content
        content = ""
        content_elem = item.select_one('.content')
        if content_elem:
            content = content_elem.get_text(strip=True)
        
        # Extract metadata
        metadata = ""
        info_elem = item.select_one('.info')
        if info_elem:
            spans = info_elem.find_all('span')
            metadata = " | ".join([span.get_text(strip=True) for span in spans])
        
        # Combine content
        full_content = content
        if metadata:
            full_content += f"\n📅 {metadata}"
        
        # Construct URL - THIS IS THE KEY FIX
        article_url = f"{self.base_url}/ArticleDetail.do?articleID={article_id}"
        
        return {
            'title': title,
            'content': full_content[:350],
            'url': article_url,
            'article_id': article_id,
            'onclick_handler': onclick,
            'is_live_scrape': live,
            'metadata': {
                'source': self.display_name,
                'scraped_at': datetime.now().isoformat(),
                'scrape_method': 'live' if live else 'local'
            }
        }
    
    def _enhance_with_session_info(self, article: Dict[str, Any]) -> Dict[str, Any]:
        """Add session guidance to article content"""
        article_id = article.get('article_id', '')
        is_live = article.get('is_live_scrape', False)
        content = article.get('content', '')
        
        # Only add guidance for non-live scrapes or as general info
        if not is_live:
            guidance = f"\n\n🔐 <b>링크 접속 방법:</b>"
            guidance += f"\n• 먼저 adiga.kr 방문 (세션 필요)"
            guidance += f"\n• 직접 링크: {article['url']}"
            guidance += f"\n• JavaScript: fnDetailPopup('{article_id}')"
            guidance += f"\n• 세션 유지가 필요합니다"
            
            # Add to content if not too long
            if len(content) + len(guidance) < 400:
                article['content'] = content + guidance
        
        # Add session metadata
        article['metadata']['requires_session'] = True
        article['metadata']['cookies_required'] = True
        
        return article
    
    def parse_article(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """Parse raw article data"""
        try:
            article_id = raw_data.get('article_id', '')
            title = raw_data.get('title', '')
            content = raw_data.get('content', '')
            url = raw_data.get('url', '')
            metadata = raw_data.get('metadata', {})
            
            # Extract additional info
            publish_date = self._extract_publish_date(content)
            university = self._extract_university(title)
            
            article = {
                'id': f"adiga_session_{article_id}",
                'title': title,
                'content': content,
                'url': url,
                'source': self.name,
                'scraped_at': datetime.now().isoformat(),
                'published_date': publish_date.isoformat() if publish_date else None,
                'university': university,
                'department': self._extract_department(title, content),
                'metadata': {
                    **metadata,
                    'article_id': article_id,
                    'session_based': True,
                    'direct_link': url
                }
            }
            
            return article
            
        except Exception as e:
            self.logger.error(f"Parse error: {e}")
            return {
                'id': f"adiga_error_{datetime.now().timestamp()}",
                'title': "Parse Error",
                'content': str(e),
                'url': '',
                'source': self.name,
                'scraped_at': datetime.now().isoformat(),
                'metadata': {'error': True}
            }
    
    def _extract_publish_date(self, content: str) -> Optional[datetime]:
        """Extract publish date"""
        date_patterns = [
            r'(\d{4})년\s*(\d{1,2})월\s*(\d{1,2})일',
            r'(\d{4}-\d{2}-\d{2})',
            r'(\d{4})\.(\d{2})\.(\d{2})'
        ]
        
        for pattern in date_patterns:
            match = re.search(pattern, content)
            if match:
                try:
                    date_str = match.group(0)
                    if '년' in date_str:
                        year = int(match.group(1))
                        month = int(match.group(2))
                        day = int(match.group(3))
                        return datetime(year, month, day)
                    elif '-' in date_str:
                        return datetime.fromisoformat(date_str)
                    elif '.' in date_str:
                        year = int(match.group(1))
                        month = int(match.group(2))
                        day = int(match.group(3))
                        return datetime(year, month, day)
                except (ValueError, IndexError):
                    continue
        
        return None
    
    def _extract_university(self, title: str) -> Optional[str]:
        """Extract university name"""
        univ_patterns = [
            (r'서울대', '서울대학교'),
            (r'연세대', '연세대학교'),
            (r'고려대', '고려대학교'),
            (r'성균관대', '성균관대학교'),
            (r'한양대', '한양대학교'),
            (r'서강대', '서강대학교'),
            (r'이화여대', '이화여자대학교'),
            (r'중앙대', '중앙대학교'),
            (r'경희대', '경희대학교'),
            (r'한국외대', '한국외국어대학교')
        ]
        
        for pattern, full_name in univ_patterns:
            if re.search(pattern, title):
                return full_name
        
        return None
    
    def _extract_department(self, title: str, content: str) -> Optional[str]:
        """Extract department"""
        text_to_check = f"{title} {content}".lower()
        
        department_keywords = {
            'music': ['음악', '실용음악', '성악', '작곡'],
            'korean': ['한국어', '국어', '국어국문', '국문학'],
            'english': ['영어', '영어영문', '영문학'],
            'liberal': ['인문', '인문학', '교양', '교양교육']
        }
        
        for dept, keywords in department_keywords.items():
            for keyword in keywords:
                if keyword in text_to_check:
                    return dept
        
        return None
    
    def _get_fallback_articles(self) -> List[Dict[str, Any]]:
        """Fallback articles"""
        self.logger.warning("Using fallback articles")
        return [
            {
                'title': '[입시의 정석] 정시 등록 오늘부터…이중 등록 유의해야',
                'content': '정시 등록이 오늘부터 시작됩니다. 대학별 등록 마감일 확인.',
                'url': 'https://adiga.kr/ArticleDetail.do?articleID=26546',
                'article_id': '26546',
                'is_live_scrape': False,
                'metadata': {
                    'source': self.display_name,
                    'scraped_at': datetime.now().isoformat(),
                    'is_fallback': True
                }
            }
        ]
    
    def cleanup(self):
        """Cleanup session"""
        if self._session:
            self._session.close()
            self._session = None
            self.logger.debug("Session closed")


# Legacy compatibility wrapper
class LegacyAdigaScraper:
    """Wrapper for backward compatibility"""
    
    def __init__(self):
        config = {
            'name': 'adiga',
            'base_url': 'https://adiga.kr',
            'html_file_path': 'adiga_structure.html',
            'max_articles': 10,
            'display_name': 'Adiga Session (어디가)',
            'timeout': 30,
            'retry_attempts': 3
        }
        self._scraper = AdigaScraper(config)
        self.source_name = self._scraper.display_name
        self.source_config = self._scraper.source_config
    
    def scrape(self):
        return self._scraper.scrape()
    
    def find_new_programs(self, current_programs):
        return self._scraper.find_new_programs(current_programs)
    
    def save_detected(self, programs):
        return self._scraper.save_detected(programs)


# Test
if __name__ == "__main__":
    print("Testing AdigaScraper with Session Support")
    print("=" * 60)
    
    scraper = AdigaScraper()
    
    try:
        articles = scraper.fetch_articles()
        print(f"Fetched {len(articles)} articles")
        
        if articles:
            print("\nSample article:")
            print(f"Title: {articles[0].get('title', 'Unknown')}")
            print(f"URL: {articles[0].get('url', 'No URL')}")
            print(f"Live scrape: {articles[0].get('is_live_scrape', False)}")
            print(f"Content preview: {articles[0].get('content', '')[:100]}...")
            
            # Test parsing
            parsed = scraper.parse_article(articles[0])
            print(f"\nParsed ID: {parsed.get('id')}")
            print(f"Metadata: {parsed.get('metadata', {})}")
        
        print("\n" + "=" * 60)
        print("Session-based scraper ready!")
        
    finally:
        scraper.cleanup()
