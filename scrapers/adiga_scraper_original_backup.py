#!/usr/bin/env python3
"""
Adiga.kr Scraper that extracts ACTUAL article content from hidden field
"""
import re
import requests
import html
from typing import List, Dict, Any, Optional
from bs4 import BeautifulSoup
from datetime import datetime
import os
import sys

# Add the parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.base_scraper import BaseScraper


class AdigaScraper(BaseScraper):
    """Adiga.kr scraper that extracts actual article content."""
    
    def __init__(self, config: Dict[str, Any] = None):
        if config is None:
            config = {
                'name': 'adiga',
                'base_url': 'https://adiga.kr',
                'html_file_path': 'adiga_structure.html',
                'max_articles': 10,
                'display_name': 'Adiga (어디가)',
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
        self.display_name = config.get('display_name', 'Adiga (어디가)')
        
        # URLs
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
        
        self.logger.info(f"Initialized {self.display_name} with content extraction")
    
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
        self.logger.info(f"Fetching articles with content extraction")
        
        try:
            # Try live AJAX
            live_articles = self._fetch_live_articles_ajax()
            if live_articles:
                # For live articles, we need to fetch each article's content
                articles_with_content = []
                for article in live_articles:
                    try:
                        enhanced = self._enhance_with_actual_content(article)
                        articles_with_content.append(enhanced)
                    except Exception as e:
                        self.logger.warning(f"Failed to enhance article: {e}")
                        articles_with_content.append(article)
                return articles_with_content
            else:
                # Fallback to local
                return self._parse_local_html()
                
        except Exception as e:
            self.logger.error(f"Fetch error: {e}")
            return self._parse_local_html()
    
    def _enhance_with_actual_content(self, article: Dict[str, Any]) -> Dict[str, Any]:
        """
        Fetch actual article content from detail page
        """
        url = article.get('url')
        if not url:
            return article
        
        try:
            self.logger.debug(f"Fetching content from: {url}")
            response = self.session.get(url, timeout=10, allow_redirects=True)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Extract hidden content from lnaCn1 input
                hidden_input = soup.find('input', {'id': 'lnaCn1'})
                if hidden_input and hidden_input.get('value'):
                    hidden_html = hidden_input['value']
                    
                    # Decode HTML entities
                    decoded_html = html.unescape(hidden_html)
                    
                    # Parse the decoded HTML to extract text
                    content_soup = BeautifulSoup(decoded_html, 'html.parser')
                    
                    # Remove scripts and styles
                    for script in content_soup(["script", "style"]):
                        script.decompose()
                    
                    # Get clean text
                    clean_text = content_soup.get_text()
                    
                    # Clean up the text
                    lines = [line.strip() for line in clean_text.split('\n') if line.strip()]
                    clean_content = ' '.join(lines[:10])  # First 10 lines
                    
                    if clean_content and len(clean_content) > 50:
                        # Replace preview with actual content
                        article['content'] = clean_content[:500]  # Limit length
                        article['metadata']['has_actual_content'] = True
                        article['metadata']['content_source'] = 'detail_page'
                        self.logger.debug(f"Extracted {len(clean_content)} chars of actual content")
                    else:
                        self.logger.debug("No substantial content extracted")
                
                # Also extract visible content
                visible_content = self._extract_visible_content(soup)
                if visible_content and 'content' not in article.get('metadata', {}).get('content_source', ''):
                    article['content'] = visible_content[:500]
                    article['metadata']['has_actual_content'] = True
                    article['metadata']['content_source'] = 'visible_page'
                
        except Exception as e:
            self.logger.warning(f"Failed to enhance article content: {e}")
        
        return article
    
    def _extract_visible_content(self, soup) -> str:
        """Extract visible text from page"""
        try:
            # Remove scripts and styles
            for script in soup(["script", "style", "input", "textarea"]):
                script.decompose()
            
            # Get text and clean
            text = soup.get_text()
            lines = [line.strip() for line in text.split('\n') if line.strip()]
            
            # Filter out very short lines and navigation
            content_lines = []
            for line in lines:
                if len(line) > 20 and not any(x in line for x in ['공통', '메뉴', '로그인', '검색']):
                    content_lines.append(line)
            
            return ' '.join(content_lines[:10])  # First 10 content lines
            
        except Exception as e:
            self.logger.debug(f"Visible content extraction failed: {e}")
            return ""
    
    # Keep other methods the same as adiga_scraper_url_fixed.py
    def _fetch_live_articles_ajax(self) -> List[Dict[str, Any]]:
        """Same as before..."""
        try:
            self.session.get(self.referer_url, timeout=10)
            
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
        """Same as before..."""
        try:
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
            
            content = ""
            content_elem = parent.select_one('.content')
            if content_elem:
                content = content_elem.get_text(strip=True)
            
            metadata = ""
            info_elem = parent.select_one('.info')
            if info_elem:
                spans = info_elem.find_all('span')
                metadata = " | ".join([span.get_text(strip=True) for span in spans])
            
            article_url = f"{self.detail_url_base}?prtlBbsId={article_id}"
            
            full_content = content
            if metadata:
                full_content += f"\n📅 {metadata}"
            
            return {
                'title': title,
                'content': full_content[:350],
                'url': article_url,
                'article_id': article_id,
                'onclick_handler': onclick,
                'is_live_scrape': True,
                'metadata': {
                    'source': self.display_name,
                    'scraped_at': datetime.now().isoformat(),
                    'scrape_method': 'ajax_live',
                    'url_pattern': 'newsDetail.do?prtlBbsId=',
                    'needs_content_enhancement': True  # Flag for enhancement
                }
            }
            
        except Exception as e:
            self.logger.debug(f"Error extracting: {e}")
            return None
    
    # Keep other methods the same...
    def _parse_local_html(self) -> List[Dict[str, Any]]:
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
        
        article_url = f"{self.detail_url_base}?prtlBbsId={article_id}"
        
        full_content = content
        if metadata:
            full_content += f"\n📅 {metadata}"
        
        return {
            'title': title,
            'content': full_content[:350],
            'url': article_url,
            'article_id': article_id,
            'onclick_handler': onclick,
            'is_live_scrape': False,
            'metadata': {
                'source': self.display_name,
                'scraped_at': datetime.now().isoformat(),
                'scrape_method': 'local_file',
                'url_pattern': 'newsDetail.do?prtlBbsId=',
                'needs_content_enhancement': True
            }
        }
    
    def parse_article(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
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
                'url': url,
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
    
    # Keep helper methods...
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
                'content': '정시 등록이 오늘부터 시작됩니다. 대학별 등록 마감일 확인. <EBS뉴스 2026-02-03 발췌>',
                'url': f"{self.detail_url_base}?prtlBbsId=26546",
                'article_id': '26546',
                'is_live_scrape': False,
                'metadata': {
                    'source': self.display_name,
                    'scraped_at': datetime.now().isoformat(),
                    'is_fallback': True,
                    'correct_url_pattern': True,
                    'has_actual_content': True
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
            'base_url': 'https://adiga.kr',
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
    print("Testing AdigaScraper with Content Extraction")
    print("=" * 60)
    
    scraper = AdigaScraper()
    
    try:
        articles = scraper.fetch_articles()
        print(f"Fetched {len(articles)} articles")
        
        if articles:
            print(f"\nFirst article:")
            print(f"Title: {articles[0].get('title', 'Unknown')}")
            print(f"URL: {articles[0].get('url', 'No URL')}")
            print(f"Content length: {len(articles[0].get('content', ''))} chars")
            print(f"Has actual content: {articles[0].get('metadata', {}).get('has_actual_content', False)}")
            print(f"Content preview: {articles[0].get('content', '')[:150]}...")
        
        print("\n" + "=" * 60)
        print("Content extraction implemented!")
        
    finally:
        scraper.cleanup()
