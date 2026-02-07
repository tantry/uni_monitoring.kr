#!/usr/bin/env python3
"""
Adiga.kr Scraper UPDATED for current HTML structure
Extracts ACTUAL article content from hidden field with proper URL structure
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
        
        # URLs - UPDATED to match actual structure
        self.detail_url_base = "https://www.adiga.kr/uct/nmg/enw/newsDetail.do"
        
        self._session = None
        
        # Backward compatibility
        self.source_config = {
            'name': self.display_name,
            'base_url': self.base_url,
            'type': 'university_admission_session'
        }
        self.source_name = self.display_name
        
        self.logger.info(f"Initialized {self.display_name} UPDATED for current HTML structure")
    
    @property
    def session(self):
        if self._session is None:
            self._session = requests.Session()
            self._session.headers.update({
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7',
                'Referer': 'https://www.adiga.kr/',
            })
        return self._session
    
    def fetch_articles(self) -> List[Dict[str, Any]]:
        """UPDATED: Fetch articles from current list-based HTML structure"""
        self.logger.info(f"Fetching articles from current HTML structure")
        
        try:
            # Parse local HTML file with updated structure
            articles = self._parse_local_html_updated()
            if articles:
                # Enhance with actual content
                articles_with_content = []
                for article in articles:
                    try:
                        enhanced = self._enhance_with_actual_content(article)
                        articles_with_content.append(enhanced)
                    except Exception as e:
                        self.logger.warning(f"Failed to enhance article: {e}")
                        articles_with_content.append(article)
                return articles_with_content
            else:
                return self._get_fallback_articles()
                
        except Exception as e:
            self.logger.error(f"Fetch error: {e}")
            return self._get_fallback_articles()
    
    def _parse_local_html_updated(self) -> List[Dict[str, Any]]:
        """UPDATED: Parse the current list-based HTML structure"""
        if not os.path.exists(self.html_file_path):
            self.logger.error(f"HTML file not found: {self.html_file_path}")
            return []
        
        try:
            with open(self.html_file_path, 'r', encoding='utf-8') as f:
                html_content = f.read()
            
            soup = BeautifulSoup(html_content, 'html.parser')
            articles = []
            
            # UPDATED: Find the ul with class uctList02
            article_list = soup.find('ul', class_='uctList02')
            if not article_list:
                self.logger.error("Could not find uctList02 container")
                return []
            
            # UPDATED: Find all li elements
            list_items = article_list.find_all('li')
            self.logger.info(f"Found {len(list_items)} article list items")
            
            for li in list_items[:self.max_articles]:
                article_data = self._extract_from_list_item(li)
                if article_data:
                    articles.append(article_data)
            
            return articles
            
        except Exception as e:
            self.logger.error(f"Error parsing HTML: {e}")
            return []
    
    def _extract_from_list_item(self, li_element) -> Optional[Dict[str, Any]]:
        """Extract article data from list item"""
        try:
            # Find anchor with onclick
            anchor = li_element.find('a', onclick=True)
            if not anchor:
                return None
            
            onclick = anchor.get('onclick', '')
            
            # Extract article ID from fnDetailPopup
            match = re.search(r'fnDetailPopup\("(\d+)"\)', onclick)
            if not match:
                return None
            
            article_id = match.group(1)
            
            # Extract title from uctCastTitle
            title_elem = anchor.find('p', class_='uctCastTitle')
            title = title_elem.get_text(strip=True) if title_elem else "No Title"
            
            # Remove "newIcon" class text if present
            title = title.replace('newIcon', '').strip()
            
            # Extract content snippet
            content_elem = anchor.find('span', class_='content')
            content_snippet = content_elem.get_text(strip=True) if content_elem else ""
            
            # Clean content snippet
            if content_snippet:
                content_snippet = re.sub(r'&lt;.*?&gt;', '', content_snippet)
                content_snippet = re.sub(r'기사 제목\s*:\s*', '', content_snippet)
                content_snippet = re.sub(r'뉴스\s*내용 전체 보기', '', content_snippet)
                content_snippet = content_snippet.strip()
            
            # Extract date from info
            info_list = anchor.find('ul', class_='info')
            date_str = datetime.now().strftime('%Y-%m-%d')
            
            if info_list:
                info_items = info_list.find_all('li')
                if len(info_items) >= 2:
                    dept_spans = info_items[1].find_all('span')
                    if len(dept_spans) >= 2:
                        date_str = dept_spans[1].get_text(strip=True)
            
            # Build URL
            url = f"{self.detail_url_base}?prtlBbsId={article_id}"
            
            return {
                'article_id': article_id,
                'title': title,
                'content': content_snippet,
                'date': date_str,
                'url': url,
                'is_live_scrape': False,
                'metadata': {
                    'source': self.display_name,
                    'scraped_at': datetime.now().isoformat(),
                    'scrape_method': 'local_file_updated',
                    'article_id': article_id,
                    'has_actual_content': False  # Will be updated when we fetch content
                }
            }
            
        except Exception as e:
            self.logger.debug(f"Error extracting from list item: {e}")
            return None
    
    def _enhance_with_actual_content(self, article: Dict[str, Any]) -> Dict[str, Any]:
        """Fetch actual content from article URL"""
        article_id = article.get('article_id', '')
        url = article.get('url', '')
        
        if not url:
            return article
        
        try:
            response = self.session.get(url, timeout=self.timeout)
            
            if response.status_code == 200:
                # Extract content from hidden field
                content = self._extract_content_from_page(response.text)
                
                if content:
                    article['content'] = content
                    article['metadata']['has_actual_content'] = True
                    article['metadata']['content_extraction_method'] = 'hidden_field'
                    article['metadata']['content_length'] = len(content)
                    self.logger.info(f"Extracted {len(content)} chars for article {article_id}")
                else:
                    # Try alternative extraction
                    soup = BeautifulSoup(response.text, 'html.parser')
                    
                    # Look for popup content
                    popup = soup.find('div', id='newsPopCont')
                    if popup:
                        content_text = popup.get_text(separator=' ', strip=True)
                        if len(content_text) > 100:
                            article['content'] = content_text[:500] + "..."
                            article['metadata']['has_actual_content'] = True
                            article['metadata']['content_extraction_method'] = 'popup_text'
                    
            else:
                self.logger.warning(f"Failed to fetch {url}: HTTP {response.status_code}")
                
        except Exception as e:
            self.logger.error(f"Error enhancing article {article_id}: {e}")
        
        return article
    
    def _extract_content_from_page(self, html_content: str) -> Optional[str]:
        """Extract content from hidden field"""
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Look for hidden input with HTML content
            hidden_input = soup.find('input', id='lnaCn1')
            if hidden_input and hidden_input.get('value'):
                html_content = hidden_input['value']
                
                # Decode HTML entities
                decoded_content = html.unescape(html_content)
                
                # Parse the inner HTML
                inner_soup = BeautifulSoup(decoded_content, 'html.parser')
                
                # Extract text
                text_content = inner_soup.get_text(separator=' ', strip=True)
                
                if text_content and len(text_content) > 50:
                    return text_content
        
        except Exception as e:
            self.logger.debug(f"Hidden field extraction failed: {e}")
        
        return None
    
    def parse_article(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """Parse article data"""
        article_id = raw_data.get('article_id', '')
        title = raw_data.get('title', 'No Title')
        url = raw_data.get('url', '')
        content = raw_data.get('content', '')
        
        # Extract university and department
        university = self._extract_university(title)
        department = self._extract_department(title, content)
        
        # Generate ID
        article_hash = f"adiga_{article_id}"
        
        # Update metadata
        metadata = raw_data.get('metadata', {})
        metadata.update({
            'university': university,
            'department': department,
            'correct_url_pattern': 'newsDetail.do?prtlBbsId=' in url,
            'url_works_with_session': True
        })
        
        return {
            'id': article_hash,
            'title': title,
            'content': content,
            'url': url,
            'published_date': raw_data.get('date'),
            'university': university,
            'department': department if department else {'name': 'general'},
            'metadata': metadata,
            'source': self.name
        }
    
    def _extract_university(self, title: str) -> Optional[str]:
        """Extract university name"""
        univ_patterns = [
            (r'서울대', '서울대학교'),
            (r'연세대', '연세대학교'),
            (r'고려대', '고려대학교'),
        ]
        
        for pattern, full_name in univ_patterns:
            if re.search(pattern, title):
                return full_name
        return None
    
    def _extract_department(self, title: str, content: str) -> Optional[str]:
        """Extract department"""
        text_to_check = f"{title} {content}".lower()
        
        dept_keywords = {
            'music': ['음악', '실용음악'],
            'korean': ['한국어', '국어'],
            'english': ['영어', '영어영문'],
        }
        
        for dept, keywords in dept_keywords.items():
            for keyword in keywords:
                if keyword in text_to_check:
                    return dept
        return None
    
    def _fetch_live_articles_ajax(self) -> List[Dict[str, Any]]:
        """Try to fetch live articles (fallback)"""
        return []
    
    def _get_fallback_articles(self) -> List[Dict[str, Any]]:
        """Get fallback articles"""
        self.logger.warning("Using fallback articles")
        return [
            {
                'article_id': '26546',
                'title': '[입시의 정석] 정시 등록 오늘부터…이중 등록 유의해야',
                'content': '정시 등록이 오늘부터 시작됩니다. 대학별 등록 마감일 확인.',
                'url': f"{self.detail_url_base}?prtlBbsId=26546",
                'date': '2026-02-04',
                'is_live_scrape': False,
                'metadata': {
                    'source': self.display_name,
                    'scraped_at': datetime.now().isoformat(),
                    'is_fallback': True
                }
            }
        ]
    
    def cleanup(self):
        """Cleanup"""
        if self._session:
            self._session.close()
            self._session = None


# Legacy compatibility wrapper - UPDATED
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
    print("Testing UPDATED Adiga Scraper")
    print("=" * 60)
    
    scraper = AdigaScraper()
    
    try:
        articles = scraper.scrape()
        print(f"Scraped {len(articles)} articles")
        
        if articles:
            for i, article in enumerate(articles[:3]):
                print(f"\n--- Article {i+1} ---")
                print(f"Title: {article.get('title')}")
                print(f"URL: {article.get('url')}")
                
                metadata = article.get('metadata', {})
                print(f"Has actual content: {metadata.get('has_actual_content', False)}")
                print(f"Content length: {len(article.get('content', ''))} chars")
                
                if metadata.get('has_actual_content'):
                    content = article.get('content', '')
                    print(f"Content preview: {content[:150]}...")
        
        print("\n" + "=" * 60)
        
    finally:
        scraper.cleanup()
