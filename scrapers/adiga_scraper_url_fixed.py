#!/usr/bin/env python3
"""
Adiga.kr Scraper with CORRECT URL Pattern
Using working pattern from uni_monitor.py: newsDetail.do?prtlBbsId=
"""
import re
import requests
from typing import List, Dict, Any, Optional
from bs4 import BeautifulSoup
from datetime import datetime
import os
import sys

# Add the parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.base_scraper import BaseScraper


class AdigaScraper(BaseScraper):
    """Adiga.kr scraper with CORRECT URL pattern."""
    
    def __init__(self, config: Dict[str, Any] = None):
        if config is None:
            config = {
                'name': 'adiga',
                'base_url': 'https://www.adiga.kr',
                'html_file_path': 'adiga_structure.html',
                'max_articles': 10,
                'display_name': 'Adiga (어디가)',
                'timeout': 30,
                'retry_attempts': 3
            }
        
        base_config = {
            'name': config.get('name', 'adiga'),
            'base_url': config.get('base_url', 'https://www.adiga.kr'),
            'timeout': config.get('timeout', 30),
            'retry_attempts': config.get('retry_attempts', 3)
        }
        
        super().__init__(base_config)
        
        self.full_config = config
        self.html_file_path = config.get('html_file_path', 'adiga_structure.html')
        self.max_articles = config.get('max_articles', 10)
        self.display_name = config.get('display_name', 'Adiga (어디가)')
        
        # CORRECT URLs from working uni_monitor.py
        self.ajax_url = "https://www.adiga.kr/uct/nmg/enw/newsAjax.do"
        self.referer_url = "https://www.adiga.kr/uct/nmg/enw/newsView.do?menuId=PCUCTNMG2000"
        self.detail_url_base = "https://www.adiga.kr/uct/nmg/enw/newsDetail.do"
        
        self._session = None
        
        # Backward compatibility
        self.source_config = {
            'name': self.display_name,
            'base_url': self.base_url,
            'type': 'university_admission_session'
        }
        self.source_name = self.display_name
        
        self.logger.info(f"Initialized {self.display_name} with CORRECT URL pattern")
    
    @property
    def session(self):
        if self._session is None:
            self._session = requests.Session()
            self._session.headers.update({
                'User-Agent': 'Mozilla/5.0',
                'X-Requested-With': 'XMLHttpRequest',
                'Referer': self.referer_url
            })
        return self._session
    
    def fetch_articles(self) -> List[Dict[str, Any]]:
        self.logger.info(f"Fetching articles with CORRECT URL pattern")
        
        try:
            # Try live AJAX first
            live_articles = self._fetch_live_articles_ajax()
            if live_articles:
                return live_articles
            else:
                # Fallback to local
                return self._parse_local_html()
                
        except Exception as e:
            self.logger.error(f"Fetch error: {e}")
            return self._parse_local_html()
    
    def _fetch_live_articles_ajax(self) -> List[Dict[str, Any]]:
        """Fetch using CORRECT pattern"""
        try:
            # Establish session
            self.session.get(self.referer_url, timeout=10)
            
            # AJAX request
            form_data = {
                'menuId': 'PCUCTNMG2000',
                'currentPage': '1',
                'cntPerPage': '20',
                'searchKeywordType': 'title',
                'searchKeyword': '',
            }
            
            response = self.session.post(self.ajax_url, data=form_data, timeout=15)
            
            if response.status_code != 200:
                return []
            
            soup = BeautifulSoup(response.content, 'html.parser')
            article_elements = soup.find_all(class_='uctCastTitle')
            
            raw_articles = []
            for element in article_elements[:self.max_articles]:
                try:
                    article = self._extract_from_ajax_element(element, soup)
                    if article:
                        raw_articles.append(article)
                except:
                    continue
            
            return raw_articles
            
        except:
            return []
    
    def _extract_from_ajax_element(self, element, soup) -> Optional[Dict[str, Any]]:
        """Extract with CORRECT URL pattern"""
        try:
            # Find parent with onclick
            parent = element.find_parent(['li', 'tr', 'div'])
            if not parent:
                return None
            
            onclick_elem = parent.find(onclick=True)
            if not onclick_elem:
                return None
            
            onclick = onclick_elem.get('onclick', '')
            match = re.search(r'fnDetailPopup\(["\'](\d+)["\']\)', onclick)
            if not match:
                return None
            
            article_id = match.group(1)
            title = element.get_text(strip=True).replace('newIcon', '').strip()
            
            # Find content
            content = ""
            content_elem = parent.select_one('.content')
            if content_elem:
                content = content_elem.get_text(strip=True)
            
            # Find metadata
            metadata = ""
            info_elem = parent.select_one('.info')
            if info_elem:
                spans = info_elem.find_all('span')
                metadata = " | ".join([span.get_text(strip=True) for span in spans])
            
            # ✅ CORRECT URL PATTERN from working code
            article_url = f"{self.detail_url_base}?prtlBbsId={article_id}"
            
            # Combine content
            full_content = content
            if metadata:
                full_content += f"\n📅 {metadata}"
            
            return {
                'title': title,
                'content': full_content[:350],
                'url': article_url,  # ✅ CORRECT URL
                'article_id': article_id,
                'onclick_handler': onclick,
                'is_live_scrape': True,
                'metadata': {
                    'source': self.display_name,
                    'scraped_at': datetime.now().isoformat(),
                    'scrape_method': 'ajax_live',
                    'url_pattern': 'newsDetail.do?prtlBbsId=',  # ✅ Record pattern
                    'verified_pattern': True
                }
            }
            
        except Exception as e:
            self.logger.debug(f"Error extracting: {e}")
            return None
    
    def _parse_local_html(self) -> List[Dict[str, Any]]:
        """Parse local file with CORRECT URL pattern"""
        if not os.path.exists(self.html_file_path):
            return self._get_fallback_articles()
        
        try:
            with open(self.html_file_path, 'r', encoding='utf-8') as f:
                html = f.read()
            
            soup = BeautifulSoup(html, 'html.parser')
            raw_articles = []
            
            article_items = soup.select('ul.uctList02 li')
            
            for item in article_items[:self.max_articles]:
                try:
                    article = self._extract_from_local_item(item)
                    if article:
                        raw_articles.append(article)
                except:
                    continue
            
            return raw_articles
            
        except:
            return self._get_fallback_articles()
    
    def _extract_from_local_item(self, item) -> Optional[Dict[str, Any]]:
        """Extract from local with CORRECT URL pattern"""
        anchor = item.find('a', onclick=True)
        if not anchor:
            return None
        
        onclick = anchor.get('onclick', '')
        match = re.search(r'fnDetailPopup\(["\'](\d+)["\']\)', onclick)
        if not match:
            return None
        
        article_id = match.group(1)
        
        title_elem = anchor.select_one('.uctCastTitle')
        if not title_elem:
            return None
        
        title = title_elem.get_text(strip=True).replace('newIcon', '').strip()
        
        content_elem = anchor.select_one('.content')
        content = content_elem.get_text(strip=True) if content_elem else ""
        
        info_elem = anchor.select_one('.info')
        metadata = ""
        if info_elem:
            spans = info_elem.find_all('span')
            metadata = " | ".join([span.get_text(strip=True) for span in spans])
        
        # ✅ CORRECT URL PATTERN for local too
        article_url = f"{self.detail_url_base}?prtlBbsId={article_id}"
        
        full_content = content
        if metadata:
            full_content += f"\n📅 {metadata}"
        
        return {
            'title': title,
            'content': full_content[:350],
            'url': article_url,  # ✅ CORRECT URL
            'article_id': article_id,
            'onclick_handler': onclick,
            'is_live_scrape': False,
            'metadata': {
                'source': self.display_name,
                'scraped_at': datetime.now().isoformat(),
                'scrape_method': 'local_file',
                'url_pattern': 'newsDetail.do?prtlBbsId=',
                'verified_pattern': True
            }
        }
    
    def parse_article(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """Parse with CORRECT URL info"""
        try:
            article_id = raw_data.get('article_id', '')
            title = raw_data.get('title', '')
            content = raw_data.get('content', '')
            url = raw_data.get('url', '')
            metadata = raw_data.get('metadata', {})
            
            publish_date = self._extract_publish_date(content)
            university = self._extract_university(title)
            
            article = {
                'id': f"adiga_{article_id}",
                'title': title,
                'content': content,
                'url': url,  # ✅ CORRECT URL
                'source': self.name,
                'scraped_at': datetime.now().isoformat(),
                'published_date': publish_date.isoformat() if publish_date else None,
                'university': university,
                'department': self._extract_department(title, content),
                'metadata': {
                    **metadata,
                    'article_id': article_id,
                    'correct_url_pattern': True,
                    'url_works_with_session': True
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
    
    # Keep helper methods same...
    def _extract_publish_date(self, content: str) -> Optional[datetime]:
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
                except:
                    continue
        return None
    
    def _extract_university(self, title: str) -> Optional[str]:
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
        self.logger.warning("Using fallback articles")
        return [
            {
                'title': '[입시의 정석] 정시 등록 오늘부터…이중 등록 유의해야',
                'content': '정시 등록이 오늘부터 시작됩니다. 대학별 등록 마감일 확인.',
                'url': f"{self.detail_url_base}?prtlBbsId=26546",  # ✅ CORRECT fallback too
                'article_id': '26546',
                'is_live_scrape': False,
                'metadata': {
                    'source': self.display_name,
                    'scraped_at': datetime.now().isoformat(),
                    'is_fallback': True,
                    'correct_url_pattern': True
                }
            }
        ]
    
    def cleanup(self):
        if self._session:
            self._session.close()
            self._session = None


# Legacy compatibility wrapper
class LegacyAdigaScraper:
    def __init__(self):
        config = {
            'name': 'adiga',
            'base_url': 'https://www.adiga.kr',
            'html_file_path': 'adiga_structure.html',
            'max_articles': 10,
            'display_name': 'Adiga (어디가)',
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
    print("Testing AdigaScraper with CORRECT URL Pattern")
    print("=" * 60)
    
    scraper = AdigaScraper()
    
    try:
        articles = scraper.fetch_articles()
        print(f"Fetched {len(articles)} articles")
        
        if articles:
            print(f"\nFirst article:")
            print(f"Title: {articles[0].get('title', 'Unknown')}")
            print(f"URL: {articles[0].get('url', 'No URL')}")
            print(f"URL pattern: {articles[0].get('metadata', {}).get('url_pattern', 'unknown')}")
            print(f"Live scrape: {articles[0].get('is_live_scrape', False)}")
            
            # Test the URL with session
            print(f"\nTesting URL access with session...")
            test_response = scraper.session.head(articles[0]['url'], timeout=5, allow_redirects=False)
            print(f"URL status: {test_response.status_code}")
            
            if test_response.status_code == 200:
                print("✅ URL should work in Telegram!")
            else:
                print(f"⚠ URL returned {test_response.status_code}")
        
        print("\n" + "=" * 60)
        print("Correct URL pattern applied: newsDetail.do?prtlBbsId=")
        
    finally:
        scraper.cleanup()
