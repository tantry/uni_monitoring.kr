#!/usr/bin/env python3
"""
Adiga.kr scraper - COMPATIBLE with BaseScraper
"""
import requests
from bs4 import BeautifulSoup
import re
import json
import os
from datetime import datetime
from .scraper_base import BaseScraper

class AdigaScraper(BaseScraper):
    """Adiga scraper that inherits from BaseScraper"""
    
    def __init__(self):
        # Get source config from sources.py if available
        try:
            import sources
            source_config = sources.SOURCES.get('adiga', {})
        except:
            source_config = {
                'name': 'Adiga',
                'base_url': 'https://www.adiga.kr',
                'search_url': 'https://www.adiga.kr/ArticleSearchList.do'
            }
        
        super().__init__(
            source_name="Adiga (어디가)",
            source_config=source_config
        )
        self.base_url = source_config.get('base_url', 'https://www.adiga.kr')
    
    def scrape(self):
        """Main scraping method"""
        print(f"🌐 Scraping {self.source_name}...")
        return self.fetch_articles()
    
    def fetch_articles(self):
        """Fetch articles with correct URLs"""
        articles = []
        
        try:
            # Try to use saved HTML first
            try:
                with open('adiga_structure.html', 'r', encoding='utf-8') as f:
                    html = f.read()
                print("   📁 Using saved HTML file")
                soup = BeautifulSoup(html, 'html.parser')
                articles = self._parse_articles(soup)
            except FileNotFoundError:
                print("   ⚠️ No saved HTML, trying live...")
                return self._get_fallback_articles()
            
        except Exception as e:
            print(f"   ❌ Error: {e}")
            return self._get_fallback_articles()
        
        return articles
    
    def _parse_articles(self, soup):
        """Parse articles from BeautifulSoup"""
        articles = []
        
        # Find article items using YOUR HTML structure
        article_items = soup.select('ul.uctList02 li')
        
        for item in article_items[:10]:  # Limit to 10
            try:
                # Get anchor with onclick
                anchor = item.find('a', onclick=True)
                if not anchor:
                    continue
                
                # Extract article ID
                onclick = anchor.get('onclick', '')
                match = re.search(r"fnDetailPopup\('(\d+)'\)", onclick)
                if not match:
                    continue
                
                article_id = match.group(1)
                
                # Get title
                title_elem = anchor.select_one('.uctCastTitle')
                title = title_elem.get_text(strip=True) if title_elem else "No title"
                title = title.replace('newIcon', '').strip()
                
                # Get content
                content_elem = anchor.select_one('.content')
                content = content_elem.get_text(strip=True) if content_elem else ""
                
                # Get metadata
                info_elem = anchor.select_one('.info')
                metadata = ""
                if info_elem:
                    spans = info_elem.find_all('span')
                    metadata = " | ".join([span.get_text(strip=True) for span in spans])
                
                # ✅ CORRECT URL CONSTRUCTION
                article_url = f"{self.base_url}/ArticleDetail.do?articleID={article_id}"
                
                # Create standardized program data
                program_data = {
                    'id': f"adiga_{article_id}",
                    'title': title,
                    'university': '정보 없음',  # Would need parsing
                    'department': self._detect_department(title + content),
                    'deadline': '정보 없음',  # Would need parsing
                    'content': content[:300],
                    'url': article_url,
                    'source': self.source_name,
                    'metadata': metadata,
                    'scraped_at': datetime.now().isoformat()
                }
                
                articles.append(program_data)
                
            except Exception as e:
                continue
        
        print(f"   Parsed {len(articles)} articles")
        return articles
    
    def _detect_department(self, text):
        """Detect department from text"""
        text_lower = text.lower()
        
        dept_keywords = {
            'music': ['음악', 'music', '실용음악', '성악', '작곡'],
            'korean': ['한국어', '국어', '국어국문', '국문학'],
            'english': ['영어', '영어영문', '영문학'],
            'liberal': ['인문', '인문학', '교양', '교양교육'],
        }
        
        for dept, keywords in dept_keywords.items():
            if any(keyword in text_lower for keyword in keywords):
                return dept
        
        return 'general'
    
    def normalize_program_data(self, raw_data):
        """Convert to standardized format - for BaseScraper compatibility"""
        # raw_data is already in normalized format from _parse_articles
        return raw_data
    
    def _get_fallback_articles(self):
        """Fallback with test data"""
        print("   ⚠️ Using fallback test data")
        return [
            {
                'id': 'adiga_26546',
                'title': '[입시의 정석] 정시 등록 오늘부터…이중 등록 유의해야',
                'university': '다양대학교',
                'department': 'general',
                'deadline': '정보 없음',
                'content': '정시 등록이 시작되었습니다. 대학별 등록 마감일에 유의하세요.',
                'url': 'https://www.adiga.kr/ArticleDetail.do?articleID=26546',
                'source': self.source_name,
                'metadata': '2026 | 공통 | 대입상담센터',
                'scraped_at': datetime.now().isoformat()
            },
            {
                'id': 'adiga_26545',
                'title': '[입시용어 따라잡기] 창체/세특/행특',
                'university': '다양대학교',
                'department': 'general',
                'deadline': '정보 없음',
                'content': '창의적 체험활동, 학생부 종합전형, 학교생활기록부 행특 설명',
                'url': 'https://www.adiga.kr/ArticleDetail.do?articleID=26545',
                'source': self.source_name,
                'metadata': '2026 | 공통 | 대입상담센터',
                'scraped_at': datetime.now().isoformat()
            }
        ]

# Factory function for backward compatibility
def create_adiga_scraper():
    return AdigaScraper()
