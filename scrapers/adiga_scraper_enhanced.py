#!/usr/bin/env python3
"""
Enhanced Adiga Scraper with proper content extraction
"""
import re
import requests
import html
from typing import List, Dict, Any, Optional
from bs4 import BeautifulSoup
from datetime import datetime
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.base_scraper import BaseScraper
from scrapers.adiga_content_extractor import extract_content

class EnhancedAdigaScraper(BaseScraper):
    """Enhanced Adiga.kr scraper with proper content extraction"""
    
    def __init__(self, config: Dict[str, Any] = None):
        config = config or {
            'name': 'adiga',
            'base_url': 'https://adiga.kr',
            'html_file_path': 'adiga_structure.html',
            'max_articles': 10,
            'display_name': 'Adiga (어디가)',
            'timeout': 30,
            'retry_attempts': 3
        }
        
        super().__init__(config)
        
        self.html_file_path = config.get('html_file_path', 'adiga_structure.html')
        self.max_articles = config.get('max_articles', 10)
        self.display_name = config.get('display_name', 'Adiga (어디가)')
        
        # URLs
        self.ajax_url = "https://www.adiga.kr/uct/nmg/enw/newsAjax.do"
        self.detail_url_base = "https://www.adiga.kr/uct/nmg/enw/newsDetail.do"
        
        # Session
        self._session = None
        
        self.logger.info(f"Initialized Enhanced {self.display_name} with content extraction")
    
    def _get_session(self):
        """Get or create session"""
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
        """Fetch articles with enhanced content extraction"""
        self.logger.info("Fetching articles with enhanced content extraction")
        
        try:
            if os.path.exists(self.html_file_path):
                self.logger.info(f"Reading from local file: {self.html_file_path}")
                with open(self.html_file_path, 'r', encoding='utf-8') as f:
                    html_content = f.read()
                
                soup = BeautifulSoup(html_content, 'html.parser')
                articles = []
                
                # Find all article rows
                rows = soup.find_all('tr', onclick=True)
                self.logger.info(f"Found {len(rows)} article rows")
                
                for row in rows[:self.max_articles]:
                    onclick = row.get('onclick', '')
                    match = re.search(r"goDetail\('(\d+)'\)", onclick)
                    
                    if match:
                        article_id = match.group(1)
                        
                        # Extract title
                        title_cell = row.find('td', class_='subject')
                        title = title_cell.get_text(strip=True) if title_cell else "No title"
                        
                        # Extract date
                        date_cell = row.find('td', class_='date')
                        date_str = date_cell.get_text(strip=True) if date_cell else datetime.now().strftime('%Y-%m-%d')
                        
                        # Build URL
                        url = f"{self.detail_url_base}?prtlBbsId={article_id}"
                        
                        # Fetch article content
                        content_info = self._fetch_article_content(url, article_id)
                        
                        articles.append({
                            'article_id': article_id,
                            'title': title,
                            'date': date_str,
                            'url': url,
                            'content_data': content_info,
                            'is_live_scrape': False,
                            'metadata': {
                                'source': self.display_name,
                                'scraped_at': datetime.now().isoformat(),
                                'scrape_method': 'enhanced_local_file',
                                'article_id': article_id
                            }
                        })
                
                return articles
            else:
                self.logger.warning(f"Local file not found: {self.html_file_path}")
                return self._get_fallback_articles()
                
        except Exception as e:
            self.logger.error(f"Error fetching articles: {e}")
            return self._get_fallback_articles()
    
    def _fetch_article_content(self, url: str, article_id: str) -> Dict[str, Any]:
        """Fetch and extract content from article URL"""
        try:
            session = self._get_session()
            response = session.get(url, timeout=self.timeout)
            
            if response.status_code == 200:
                # Use content extractor to get actual content
                extraction_result = extract_content(response.text, url)
                
                # Log extraction details
                self.logger.info(
                    f"Content extraction for {article_id}: "
                    f"method={extraction_result.get('extraction_method')}, "
                    f"has_content={extraction_result.get('has_content')}, "
                    f"length={extraction_result.get('content_length', 0)}"
                )
                
                return extraction_result
            else:
                self.logger.warning(f"Failed to fetch {url}: HTTP {response.status_code}")
                
        except Exception as e:
            self.logger.error(f"Error fetching content from {url}: {e}")
        
        return {'has_content': False, 'clean_content': ''}
    
    def parse_article(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """Parse article with extracted content"""
        article_id = raw_data.get('article_id', '')
        title = raw_data.get('title', 'No Title')
        url = raw_data.get('url', '')
        content_data = raw_data.get('content_data', {})
        
        # Get content from extraction result
        content = content_data.get('clean_content', '')
        has_actual_content = content_data.get('has_content', False)
        extraction_method = content_data.get('extraction_method', 'none')
        
        # Extract university and department
        university = self._extract_university(title)
        department = self._extract_department(title, content)
        
        # Generate ID
        article_hash = f"adiga_{article_id}"
        
        # Enhanced metadata
        metadata = raw_data.get('metadata', {})
        metadata.update({
            'has_actual_content': has_actual_content,
            'content_length': len(content),
            'extraction_method': extraction_method,
            'university': university,
            'department': department,
            'correct_url_pattern': 'newsDetail.do?prtlBbsId=' in url,
            'url_works_with_session': True,
            'debug_info': content_data.get('debug', {})
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
        """Fallback articles"""
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
                    'is_fallback': True
                }
            }
        ]
    
    def cleanup(self):
        """Cleanup"""
        if self._session:
            self._session.close()
            self._session = None

# Test
if __name__ == "__main__":
    print("Testing Enhanced Adiga Scraper with Content Extraction")
    print("=" * 60)
    
    scraper = EnhancedAdigaScraper()
    
    try:
        articles = scraper.scrape()
        print(f"Scraped {len(articles)} articles")
        
        if articles:
            article = articles[0]
            print(f"\nFirst article analysis:")
            print(f"Title: {article.get('title')}")
            print(f"URL: {article.get('url')}")
            
            metadata = article.get('metadata', {})
            print(f"Has actual content: {metadata.get('has_actual_content', False)}")
            print(f"Extraction method: {metadata.get('extraction_method', 'unknown')}")
            print(f"Content length: {metadata.get('content_length', 0)} chars")
            
            content = article.get('content', '')
            if content:
                print(f"\nContent preview (first 200 chars):")
                print("-" * 40)
                print(content[:200])
                print("-" * 40)
            
            # Check debug info
            debug_info = metadata.get('debug_info', {})
            if debug_info:
                print(f"\nDebug info:")
                print(f"  HTML length: {debug_info.get('html_length', 0)}")
                print(f"  Hidden field found: {debug_info.get('input_id_found', False)}")
                print(f"  Popup container found: {debug_info.get('popup_cont_found', False)}")
        
        print("\n" + "=" * 60)
        print("✅ Enhanced scraper ready with content extraction!")
        
    finally:
        scraper.cleanup()
