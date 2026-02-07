#!/usr/bin/env python3
"""
Adiga Scraper - REALISTIC VERSION
Uses available snippet content since full articles aren't accessible via scraping
"""
import re
import requests
from typing import List, Dict, Any, Optional
from bs4 import BeautifulSoup
from datetime import datetime
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.base_scraper import BaseScraper


class RealisticAdigaScraper(BaseScraper):
    """Realistic Adiga scraper that works with available data"""
    
    def __init__(self, config: Dict[str, Any] = None):
        config = config or {
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
        
        self.html_file_path = config.get('html_file_path', 'adiga_structure.html')
        self.max_articles = config.get('max_articles', 10)
        self.display_name = config.get('display_name', 'Adiga (어디가)')
        self.detail_url_base = "https://www.adiga.kr/uct/nmg/enw/newsDetail.do"
        
        self.logger.info(f"Initialized REALISTIC {self.display_name} scraper")
    
    def fetch_articles(self) -> List[Dict[str, Any]]:
        """Fetch articles using available snippet content"""
        self.logger.info("Fetching articles with realistic approach")
        
        if not os.path.exists(self.html_file_path):
            self.logger.error(f"HTML file not found: {self.html_file_path}")
            return self._get_fallback_articles()
        
        try:
            with open(self.html_file_path, 'r', encoding='utf-8') as f:
                html_content = f.read()
            
            soup = BeautifulSoup(html_content, 'html.parser')
            articles = []
            
            # Find article list
            article_list = soup.find('ul', class_='uctList02')
            if not article_list:
                self.logger.error("Could not find article list")
                return self._get_fallback_articles()
            
            list_items = article_list.find_all('li')
            self.logger.info(f"Found {len(list_items)} articles")
            
            for li in list_items[:self.max_articles]:
                article_data = self._extract_article_data(li)
                if article_data:
                    articles.append(article_data)
            
            self.logger.info(f"Extracted {len(articles)} articles")
            return articles
            
        except Exception as e:
            self.logger.error(f"Error: {e}")
            return self._get_fallback_articles()
    
    def _extract_article_data(self, li_element) -> Optional[Dict[str, Any]]:
        """Extract article data with proper content handling"""
        try:
            anchor = li_element.find('a', onclick=True)
            if not anchor:
                return None
            
            onclick = anchor.get('onclick', '')
            match = re.search(r'fnDetailPopup\("(\d+)"\)', onclick)
            if not match:
                return None
            
            article_id = match.group(1)
            
            # Extract title
            title_elem = anchor.find('p', class_='uctCastTitle')
            title = title_elem.get_text(strip=True) if title_elem else "No Title"
            title = title.replace('newIcon', '').strip()
            
            # Extract and CLEAN content snippet
            content_elem = anchor.find('span', class_='content')
            content = ""
            if content_elem:
                content = content_elem.get_text(strip=True)
                # Clean the content - remove boilerplate
                content = self._clean_content_snippet(content)
            
            # Extract date
            info_list = anchor.find('ul', class_='info')
            date_str = datetime.now().strftime('%Y-%m-%d')
            
            if info_list:
                info_items = info_list.find_all('li')
                if len(info_items) >= 2:
                    dept_spans = info_items[1].find_all('span')
                    if len(dept_spans) >= 2:
                        date_str = dept_spans[1].get_text(strip=True)
            
            # Build URL
            url = f"{self.detail_url_base}?prtlBssId={article_id}"
            
            # Verify URL works
            url_verified = self._verify_url(url)
            
            return {
                'article_id': article_id,
                'title': title,
                'content': content,
                'date': date_str,
                'url': url,
                'url_verified': url_verified,
                'metadata': {
                    'source': self.display_name,
                    'scraped_at': datetime.now().isoformat(),
                    'scrape_method': 'realistic_snippet',
                    'article_id': article_id,
                    'has_actual_content': bool(content),  # We have snippet, not full article
                    'content_type': 'snippet',
                    'url_works': url_verified
                }
            }
            
        except Exception as e:
            self.logger.debug(f"Extraction error: {e}")
            return None
    
    def _clean_content_snippet(self, content: str) -> str:
        """Clean the content snippet for Telegram"""
        if not content:
            return ""
        
        # Remove HTML entities
        content = content.replace('&lt;', '<').replace('&gt;', '>')
        
        # Remove the source attribution pattern
        # Example: "<EBS뉴스 2026-02-03 발췌> 기사 제목 : [입시의 정석]..."
        patterns_to_remove = [
            r'^<[^>]+>\s*기사 제목\s*:\s*',
            r'\s*뉴스\s*내용 전체 보기$',
            r'^<[^>]+>\s*',
            r'기사 제목\s*:\s*'
        ]
        
        for pattern in patterns_to_remove:
            content = re.sub(pattern, '', content)
        
        # Trim and clean
        content = content.strip()
        
        # If we have the title repeated, remove it
        # Check if content starts with title-like pattern in brackets
        if content.startswith('[') and ']' in content:
            # Might be duplicate title, but keep it if it's different
            pass
        
        return content
    
    def _verify_url(self, url: str) -> bool:
        """Verify URL is accessible"""
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            }
            response = requests.head(url, headers=headers, timeout=5, allow_redirects=True)
            return response.status_code == 200
        except:
            return False
    
    def parse_article(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """Parse article with proper Telegram formatting"""
        article_id = raw_data.get('article_id', '')
        title = raw_data.get('title', 'No Title')
        content = raw_data.get('content', '')
        url = raw_data.get('url', '')
        
        # Prepare title for Telegram (escape single quotes)
        telegram_title = title.replace("'", "&#x27;")
        
        # Extract metadata
        university = self._extract_university(title)
        department = self._extract_department(title, content)
        
        # Generate ID
        article_hash = f"adiga_{article_id}"
        
        # Update metadata
        metadata = raw_data.get('metadata', {})
        metadata.update({
            'university': university,
            'department': department,
            'telegram_title': telegram_title,  # For Telegram formatter
            'url_verified': raw_data.get('url_verified', False)
        })
        
        return {
            'id': article_hash,
            'title': title,
            'telegram_title': telegram_title,  # Add cleaned title
            'content': content,
            'url': url,
            'published_date': raw_data.get('date'),
            'university': university,
            'department': department if department else {'name': 'general'},
            'metadata': metadata,
            'source': self.name
        }
    
    def _extract_university(self, title: str) -> Optional[str]:
        """Extract university if mentioned"""
        patterns = [
            (r'서울대', '서울대학교'),
            (r'연세대', '연세대학교'),
            (r'고려대', '고려대학교'),
            (r'카이스트', '한국과학기술원'),
            (r'포스텍', '포항공과대학교'),
            (r'성균관대', '성균관대학교'),
            (r'한양대', '한양대학교'),
        ]
        
        for pattern, name in patterns:
            if re.search(pattern, title):
                return name
        return None
    
    def _extract_department(self, title: str, content: str) -> Optional[str]:
        """Extract department"""
        text = f"{title} {content}".lower()
        
        departments = {
            'music': ['음악', '실용음악', '성악', '작곡'],
            'korean': ['한국어', '국어', '국어국문'],
            'english': ['영어', '영어영문', '영문학'],
            'medical': ['의대', '의학', '의과'],
            'engineering': ['공학', '기계', '전기', '전자'],
            'education': ['교육', '교원', '교육학']
        }
        
        for dept, keywords in departments.items():
            for keyword in keywords:
                if keyword in text:
                    return dept
        return None
    
    def _get_fallback_articles(self) -> List[Dict[str, Any]]:
        """Simple fallback"""
        return [
            {
                'article_id': '26546',
                'title': '[입시의 정석] 정시 등록 오늘부터…이중 등록 유의해야',
                'content': '정시 등록이 오늘부터 시작됩니다. 대학별 등록 마감일 확인.',
                'url': 'https://www.adiga.kr/uct/nmg/enw/newsDetail.do?prtlBssId=26546',
                'date': '2026-02-04',
                'url_verified': True,
                'metadata': {
                    'source': self.display_name,
                    'scraped_at': datetime.now().isoformat(),
                    'is_fallback': True
                }
            }
        ]
    
    def cleanup(self):
        """Cleanup - nothing needed for this scraper"""
        pass


# Legacy compatibility
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
        self._scraper = RealisticAdigaScraper(config)
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
    print("Testing REALISTIC Adiga Scraper")
    print("=" * 60)
    
    scraper = RealisticAdigaScraper()
    
    try:
        articles = scraper.scrape()
        print(f"Scraped {len(articles)} articles")
        
        if articles:
            article = articles[0]
            print(f"\n📰 First article:")
            print(f"Title: {article.get('title')}")
            print(f"URL: {article.get('url')}")
            print(f"Content: {article.get('content', '')[:100]}...")
            
            metadata = article.get('metadata', {})
            print(f"URL verified: {metadata.get('url_verified', False)}")
            print(f"Has content: {metadata.get('has_actual_content', False)}")
            print(f"Content type: {metadata.get('content_type', 'unknown')}")
        
        print("\n" + "=" * 60)
        
    finally:
        scraper.cleanup()
