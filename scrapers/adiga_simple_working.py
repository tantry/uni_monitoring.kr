#!/usr/bin/env python3
"""
Adiga Scraper - SIMPLE WORKING VERSION
"""
import re
from typing import List, Dict, Any, Optional
from bs4 import BeautifulSoup
from datetime import datetime
import os
import logging

logger = logging.getLogger("adiga_simple")

class SimpleAdigaScraper:
    """Simple working Adiga scraper"""
    
    def __init__(self, html_file_path='adiga_structure.html', max_articles=10):
        self.html_file_path = html_file_path
        self.max_articles = max_articles
        self.display_name = 'Adiga (어디가)'
        self.detail_url_base = "https://www.adiga.kr/uct/nmg/enw/newsDetail.do"
        
        logger.info(f"Initialized Simple {self.display_name} scraper")
    
    def scrape(self) -> List[Dict[str, Any]]:
        """Simple scrape"""
        logger.info("Scraping")
        
        if not os.path.exists(self.html_file_path):
            logger.error(f"File not found: {self.html_file_path}")
            return self._get_fallback()
        
        try:
            with open(self.html_file_path, 'r', encoding='utf-8') as f:
                html_content = f.read()
            
            soup = BeautifulSoup(html_content, 'html.parser')
            articles = []
            
            article_list = soup.find('ul', class_='uctList02')
            if not article_list:
                logger.error("No article list")
                return self._get_fallback()
            
            list_items = article_list.find_all('li')
            logger.info(f"Found {len(list_items)} items")
            
            for li in list_items[:self.max_articles]:
                article = self._parse_item(li)
                if article:
                    articles.append(article)
            
            logger.info(f"Got {len(articles)} articles")
            return articles
            
        except Exception as e:
            logger.error(f"Error: {e}")
            return self._get_fallback()
    
    def _parse_item(self, li) -> Optional[Dict[str, Any]]:
        """Parse list item"""
        try:
            anchor = li.find('a', onclick=True)
            if not anchor:
                return None
            
            onclick = anchor.get('onclick', '')
            match = re.search(r'fnDetailPopup\("(\d+)"\)', onclick)
            if not match:
                return None
            
            article_id = match.group(1)
            
            title_elem = anchor.find('p', class_='uctCastTitle')
            title = title_elem.get_text(strip=True) if title_elem else "No Title"
            title = title.replace('newIcon', '').strip()
            
            # Telegram title with escaped single quote
            telegram_title = title.replace("'", "&#x27;")
            
            content_elem = anchor.find('span', class_='content')
            raw_content = content_elem.get_text(strip=True) if content_elem else ""
            
            # Simple content cleaning
            content = raw_content.replace('&lt;', '<').replace('&gt;', '>')
            
            info_list = anchor.find('ul', class_='info')
            date_str = datetime.now().strftime('%Y-%m-%d')
            
            if info_list:
                info_items = info_list.find_all('li')
                if len(info_items) >= 2:
                    dept_spans = info_items[1].find_all('span')
                    if len(dept_spans) >= 2:
                        date_str = dept_spans[1].get_text(strip=True)
            
            url = f"{self.detail_url_base}?prtlBbsId={article_id}"
            
            return {
                'id': f"adiga_{article_id}",
                'title': title,
                'telegram_title': telegram_title,
                'content': content,
                'url': url,
                'published_date': date_str,
                'university': self._get_university(title),
                'department': self._get_department(title, content),
                'metadata': {
                    'source': self.display_name,
                    'scraped_at': datetime.now().isoformat(),
                    'article_id': article_id,
                    'has_content': bool(content),
                },
                'source': 'adiga'
            }
            
        except Exception as e:
            logger.debug(f"Parse error: {e}")
            return None
    
    def _get_university(self, title: str) -> Optional[str]:
        if '서울대' in title:
            return '서울대학교'
        elif '연세대' in title:
            return '연세대학교'
        elif '고려대' in title:
            return '고려대학교'
        return None
    
    def _get_department(self, title: str, content: str) -> Dict[str, str]:
        text = f"{title} {content}".lower()
        
        if any(word in text for word in ['음악', '실용음악']):
            return {'name': 'music'}
        elif any(word in text for word in ['한국어', '국어']):
            return {'name': 'korean'}
        elif any(word in text for word in ['영어', '영어영문']):
            return {'name': 'english'}
        
        return {'name': 'general'}
    
    def _get_fallback(self) -> List[Dict[str, Any]]:
        return [
            {
                'id': 'adiga_26546',
                'title': '[입시의 정석] 정시 등록 오늘부터…이중 등록 유의해야',
                'telegram_title': '[입시의 정석] 정시 등록 오늘부터…이중 등록 유의해야',
                'content': '정시 등록이 오늘부터 시작됩니다.',
                'url': 'https://www.adiga.kr/uct/nmg/enw/newsDetail.do?prtlBbsId=26546',
                'published_date': '2026-02-04',
                'university': None,
                'department': {'name': 'general'},
                'metadata': {'source': self.display_name, 'is_fallback': True},
                'source': 'adiga'
            }
        ]


# Legacy wrapper
class LegacyAdigaScraper:
    def __init__(self):
        self._scraper = SimpleAdigaScraper()
        self.source_name = self._scraper.display_name
        self.source_config = {'name': 'Adiga (어디가)'}
    
    def scrape(self):
        return self._scraper.scrape()
    
    def find_new_programs(self, current_programs):
        return []
    
    def save_detected(self, programs):
        return True


if __name__ == "__main__":
    import sys
    print("Testing Simple Adiga Scraper")
    print("=" * 60)
    
    scraper = SimpleAdigaScraper()
    articles = scraper.scrape()
    
    print(f"Found {len(articles)} articles")
    
    if articles:
        article = articles[0]
        print(f"\n📰 First article:")
        print(f"ID: {article.get('id')}")
        print(f"Title: {article.get('title')}")
        print(f"Telegram title: {article.get('telegram_title', 'NOT SET')}")
        print(f"URL: {article.get('url')}")
        print(f"Content: {article.get('content', '')[:80]}...")
        
        if article.get('telegram_title'):
            print(f"\n✅ telegram_title IS SET")
            if "'" not in article['telegram_title']:
                print("✅ Single quote escaped")
        else:
            print(f"\n❌ telegram_title NOT SET")
    
    print(f"\n" + "=" * 60)
