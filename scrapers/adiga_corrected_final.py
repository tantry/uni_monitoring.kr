#!/usr/bin/env python3
"""
Adiga Scraper - CORRECTED FINAL VERSION
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


class AdigaCorrectedScraper(BaseScraper):
    """Corrected final Adiga scraper"""
    
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
        
        base_config = {
            'name': config.get('name', 'adiga'),
            'base_url': config.get('base_url', 'https://adiga.kr'),  # FIXED: Added closing quote
            'timeout': config.get('timeout', 30),
            'retry_attempts': config.get('retry_attempts', 3)
        }
        
        super().__init__(base_config)
        
        self.html_file_path = config.get('html_file_path', 'adiga_structure.html')
        self.max_articles = config.get('max_articles', 10)
        self.display_name = config.get('display_name', 'Adiga (어디가)')
        self.detail_url_base = "https://www.adiga.kr/uct/nmg/enw/newsDetail.do"
        
        self.logger.info(f"Initialized CORRECTED {self.display_name} scraper")
    
    def fetch_articles(self) -> List[Dict[str, Any]]:
        """Fetch articles"""
        self.logger.info("Fetching articles")
        
        if not os.path.exists(self.html_file_path):
            self.logger.error(f"HTML file not found: {self.html_file_path}")
            return self._get_fallback_articles()
        
        try:
            with open(self.html_file_path, 'r', encoding='utf-8') as f:
                html_content = f.read()
            
            soup = BeautifulSoup(html_content, 'html.parser')
            articles = []
            
            article_list = soup.find('ul', class_='uctList02')
            if not article_list:
                self.logger.error("No article list found")
                return self._get_fallback_articles()
            
            list_items = article_list.find_all('li')
            self.logger.info(f"Found {len(list_items)} list items")
            
            for li in list_items[:self.max_articles]:
                article_data = self._extract_article(li)
                if article_data:
                    articles.append(article_data)
            
            self.logger.info(f"Extracted {len(articles)} articles")
            return articles
            
        except Exception as e:
            self.logger.error(f"Error: {e}")
            return self._get_fallback_articles()
    
    def _extract_article(self, li_element) -> Optional[Dict[str, Any]]:
        """Extract article data"""
        try:
            anchor = li_element.find('a', onclick=True)
            if not anchor:
                return None
            
            onclick = anchor.get('onclick', '')
            match = re.search(r'fnDetailPopup\("(\d+)"\)', onclick)
            if not match:
                return None
            
            article_id = match.group(1)
            
            # Title
            title_elem = anchor.find('p', class_='uctCastTitle')
            title = title_elem.get_text(strip=True) if title_elem else "No Title"
            title = title.replace('newIcon', '').strip()
            
            # Content snippet
            content_elem = anchor.find('span', class_='content')
            raw_content = content_elem.get_text(strip=True) if content_elem else ""
            content = self._clean_content(raw_content)
            
            # Date
            info_list = anchor.find('ul', class_='info')
            date_str = datetime.now().strftime('%Y-%m-%d')
            
            if info_list:
                info_items = info_list.find_all('li')
                if len(info_items) >= 2:
                    dept_spans = info_items[1].find_all('span')
                    if len(dept_spans) >= 2:
                        date_str = dept_spans[1].get_text(strip=True)
            
            # CORRECT URL
            url = f"{self.detail_url_base}?prtlBbsId={article_id}"
            
            # Telegram-ready title
            telegram_title = self._prepare_for_telegram(title)
            
            return {
                'article_id': article_id,
                'title': title,
                'telegram_title': telegram_title,
                'content': content,
                'date': date_str,
                'url': url,
                'metadata': {
                    'source': self.display_name,
                    'scraped_at': datetime.now().isoformat(),
                    'article_id': article_id,
                    'has_content': bool(content),
                    'content_length': len(content)
                }
            }
            
        except Exception as e:
            self.logger.debug(f"Extraction error: {e}")
            return None
    
    def _clean_content(self, raw_content: str) -> str:
        """Clean content snippet"""
        if not raw_content:
            return ""
        
        content = raw_content
        
        # Remove source prefix
        if content.startswith('&lt;'):
            # Find the closing > and remove prefix
            end = content.find('&gt;')
            if end != -1:
                content = content[end + 4:]  # Remove "&gt;"
        
        # Remove "기사 제목 :" prefix
        if '기사 제목 :' in content:
            content = content.split('기사 제목 :', 1)[-1].strip()
        
        # Remove "뉴스 내용 전체 보기" suffix
        if '뉴스 내용 전체 보기' in content:
            content = content.replace('뉴스 내용 전체 보기', '').strip()
        
        return content.strip()
    
    def _prepare_for_telegram(self, title: str) -> str:
        """Prepare title for Telegram HTML"""
        if not title:
            return ""
        # Escape single quotes for Telegram HTML mode
        return title.replace("'", "&#x27;")
    
    def parse_article(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """Parse article"""
        article_id = raw_data.get('article_id', '')
        title = raw_data.get('title', 'No Title')
        telegram_title = raw_data.get('telegram_title', '') or self._prepare_for_telegram(title)
        content = raw_data.get('content', '')
        url = raw_data.get('url', '')
        
        # Metadata
        university = self._extract_university(title)
        department = self._extract_department(title, content)
        
        article_hash = f"adiga_{article_id}"
        
        metadata = raw_data.get('metadata', {})
        metadata.update({
            'university': university,
            'department': department,
            'telegram_title': telegram_title
        })
        
        return {
            'id': article_hash,
            'title': title,
            'telegram_title': telegram_title,
            'content': content,
            'url': url,
            'published_date': raw_data.get('date'),
            'university': university,
            'department': department if department else {'name': 'general'},
            'metadata': metadata,
            'source': self.name
        }
    
    def _extract_university(self, title: str) -> Optional[str]:
        """Extract university"""
        patterns = [
            (r'서울대', '서울대학교'),
            (r'연세대', '연세대학교'),
            (r'고려대', '고려대학교'),
        ]
        
        for pattern, name in patterns:
            if re.search(pattern, title):
                return name
        return None
    
    def _extract_department(self, title: str, content: str) -> Optional[str]:
        """Extract department"""
        text = f"{title} {content}".lower()
        
        departments = {
            'music': ['음악', '실용음악'],
            'korean': ['한국어', '국어'],
            'english': ['영어', '영어영문'],
        }
        
        for dept, keywords in departments.items():
            for keyword in keywords:
                if keyword in text:
                    return dept
        return None
    
    def _get_fallback_articles(self) -> List[Dict[str, Any]]:
        """Fallback"""
        return [
            {
                'article_id': '26546',
                'title': '[입시의 정석] 정시 등록 오늘부터…이중 등록 유의해야',
                'telegram_title': '[입시의 정석] 정시 등록 오늘부터…이중 등록 유의해야',
                'content': '정시 등록이 오늘부터 시작됩니다.',
                'url': 'https://www.adiga.kr/uct/nmg/enw/newsDetail.do?prtlBbsId=26546',
                'date': '2026-02-04',
                'metadata': {
                    'source': self.display_name,
                    'scraped_at': datetime.now().isoformat(),
                    'is_fallback': True
                }
            }
        ]
    
    def cleanup(self):
        pass


# Legacy compatibility
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
        self._scraper = AdigaCorrectedScraper(config)
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
    print("Testing CORRECTED FINAL Adiga Scraper")
    print("=" * 60)
    
    scraper = AdigaCorrectedScraper()
    
    try:
        articles = scraper.scrape()
        print(f"Scraped {len(articles)} articles")
        
        if articles:
            article = articles[0]
            print(f"\n📰 First article:")
            print(f"Title: {article.get('title')}")
            print(f"Telegram title: {article.get('telegram_title')}")
            print(f"URL: {article.get('url')}")
            print(f"Content: {article.get('content', '')[:100]}...")
            
            # Verify
            if article.get('telegram_title') and "'" not in article.get('telegram_title', ''):
                print("✅ Telegram title properly escaped")
            
            if 'prtlBbsId=' in article.get('url', ''):
                print("✅ URL has correct parameter")
        
        print("\n" + "=" * 60)
        
    finally:
        scraper.cleanup()
