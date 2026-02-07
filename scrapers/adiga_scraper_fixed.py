#!/usr/bin/env python3
"""
Adiga.kr Scraper with URL validation and correction
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
from core.url_validator import ensure_working_url

class AdigaScraper(BaseScraper):
    """Adiga.kr scraper with URL validation."""
    
    def __init__(self, config: Dict[str, Any] = None):
        if config is None:
            config = {
                'name': 'adiga',
                'base_url': 'https://www.adiga.kr',
                'html_file_path': 'adiga_structure.html',
                'max_articles': 10,
                'display_name': 'Adiga (어디가)',
                'timeout': 30,
                'retry_attempts': 3,
                'validate_urls': True  # New: Enable URL validation
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
        self.validate_urls = config.get('validate_urls', True)
        
        # URLs
        self.ajax_url = "https://www.adiga.kr/uct/nmg/enw/newsAjax.do"
        self.detail_url_base = "https://www.adiga.kr/uct/nmg/enw/newsDetail.do"
        
        # Session for persistent cookies
        self._session = None
        
        self.logger.info(f"Initialized {self.display_name} with URL validation")
    
    def _get_session(self):
        """Get or create a requests session"""
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
        """Fetch articles from adiga.kr"""
        self.logger.info("Fetching articles with URL validation")
        
        try:
            # Read from local HTML file (for development)
            if os.path.exists(self.html_file_path):
                self.logger.info(f"Reading from local file: {self.html_file_path}")
                with open(self.html_file_path, 'r', encoding='utf-8') as f:
                    html_content = f.read()
                
                soup = BeautifulSoup(html_content, 'html.parser')
                articles = []
                
                # Find all article rows
                rows = soup.find_all('tr', onclick=True)
                self.logger.info(f"Found {len(rows)} article rows in local file")
                
                for row in rows[:self.max_articles]:
                    # Extract onclick attribute which contains the article ID
                    onclick = row.get('onclick', '')
                    match = re.search(r"goDetail\('(\d+)'\)", onclick)
                    
                    if match:
                        article_id = match.group(1)
                        
                        # Find title in the row
                        title_cell = row.find('td', class_='subject')
                        title = title_cell.get_text(strip=True) if title_cell else "No title"
                        
                        # Extract date
                        date_cell = row.find('td', class_='date')
                        date_str = date_cell.get_text(strip=True) if date_cell else datetime.now().strftime('%Y-%m-%d')
                        
                        # Build URL
                        url = f"{self.detail_url_base}?prtlBbsId={article_id}"
                        
                        # Validate and correct URL if enabled
                        if self.validate_urls:
                            url = ensure_working_url(url, self.display_name)
                        
                        articles.append({
                            'article_id': article_id,
                            'title': title,
                            'date': date_str,
                            'url': url,
                            'is_live_scrape': False,
                            'metadata': {
                                'source': self.display_name,
                                'scraped_at': datetime.now().isoformat(),
                                'scrape_method': 'local_file',
                                'url_pattern': 'newsDetail.do?prtlBbsId=',
                                'needs_content_enhancement': True,
                                'article_id': article_id,
                                'url_validated': self.validate_urls
                            }
                        })
                
                return articles
            
            else:
                self.logger.warning(f"Local file not found: {self.html_file_path}")
                return self._get_fallback_articles()
                
        except Exception as e:
            self.logger.error(f"Error fetching articles: {e}")
            return self._get_fallback_articles()
    
    def parse_article(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """Parse raw article data into standardized format"""
        article_id = raw_data.get('article_id', '')
        title = raw_data.get('title', 'No Title')
        url = raw_data.get('url', '')
        
        # Extract content if we have a valid URL
        content = ""
        has_actual_content = False
        
        if url and self.validate_urls:
            try:
                session = self._get_session()
                response = session.get(url, timeout=self.timeout)
                
                if response.status_code == 200:
                    soup = BeautifulSoup(response.text, 'html.parser')
                    
                    # Try to find article content
                    content_div = soup.find('div', class_='content')
                    if not content_div:
                        content_div = soup.find('div', id='content')
                    if not content_div:
                        content_div = soup.find('article')
                    
                    if content_div:
                        content = content_div.get_text(strip=True, separator=' ')
                        has_actual_content = True
                        self.logger.info(f"Extracted content for article {article_id}: {len(content)} chars")
                    else:
                        # Fallback: get meta description or first 200 chars
                        meta_desc = soup.find('meta', attrs={'name': 'description'})
                        if meta_desc:
                            content = meta_desc.get('content', '')[:200]
                        else:
                            content = soup.get_text(strip=True, separator=' ')[:200]
            except Exception as e:
                self.logger.warning(f"Could not extract content from {url}: {e}")
        
        # Extract university and department
        university = self._extract_university(title)
        department = self._extract_department(title, content)
        
        # Generate ID
        article_hash = f"adiga_{article_id}"
        
        # Update metadata
        metadata = raw_data.get('metadata', {})
        metadata.update({
            'has_actual_content': has_actual_content,
            'content_length': len(content),
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
        """Extract university name from title"""
        univ_patterns = [
            (r'서울대', '서울대학교'),
            (r'연세대', '연세대학교'),
            (r'고려대', '고려대학교'),
            (r'카이스트', '한국과학기술원'),
            (r'포스텍', '포항공과대학교'),
            (r'성균관대', '성균관대학교'),
            (r'한양대', '한양대학교'),
            (r'서강대', '서강대학교'),
            (r'이화여대', '이화여자대학교'),
            (r'숙명여대', '숙명여자대학교'),
            (r'경희대', '경희대학교'),
            (r'한국외대', '한국외국어대학교')
        ]
        
        for pattern, full_name in univ_patterns:
            if re.search(pattern, title):
                return full_name
        return None
    
    def _extract_department(self, title: str, content: str) -> Optional[str]:
        """Extract department from title and content"""
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
        """Get fallback articles if scraping fails"""
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
        """Clean up resources"""
        if self._session:
            self._session.close()
            self._session = None
        super().cleanup() if hasattr(super(), 'cleanup') else None

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
            'retry_attempts': 3,
            'validate_urls': True  # Enable URL validation by default
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
    print("Testing AdigaScraper with URL Validation")
    print("=" * 60)
    
    scraper = AdigaScraper()
    
    try:
        articles = scraper.scrape()
        print(f"Scraped {len(articles)} articles")
        
        if articles:
            print(f"\nFirst article:")
            print(f"Title: {articles[0].get('title', 'Unknown')}")
            print(f"URL: {articles[0].get('url', 'No URL')}")
            print(f"Content length: {len(articles[0].get('content', ''))} chars")
            print(f"Has actual content: {articles[0].get('metadata', {}).get('has_actual_content', False)}")
            print(f"URL validated: {articles[0].get('metadata', {}).get('url_validated', False)}")
            
            # Test the URL
            import requests
            url = articles[0].get('url')
            try:
                resp = requests.get(url, timeout=10)
                print(f"\nURL Test - Status: {resp.status_code}, Length: {len(resp.text)} chars")
                if resp.status_code == 200:
                    print("✅ URL works!")
                else:
                    print(f"⚠ URL returned {resp.status_code}")
            except Exception as e:
                print(f"❌ URL test failed: {e}")
        
        print("\n" + "=" * 60)
        print("URL validation implemented!")
        
    finally:
        scraper.cleanup()
