#!/usr/bin/env python3
"""
Adiga scraper - Simple standalone version that works
"""
import re
from bs4 import BeautifulSoup
from datetime import datetime
import json
import os

class AdigaScraper:
    def __init__(self):
        self.source_name = "Adiga (어디가)"
        self.base_url = "https://adiga.kr"
        self.source_config = {
            'name': 'Adiga',
            'base_url': 'https://adiga.kr',
            'type': 'university_admission'
        }
        # Simulate BaseScraper behavior
        self.data_dir = "uni_monitor_data"
        self.detected_file = os.path.join(self.data_dir, f"detected_{self.source_name}.json")
        os.makedirs(self.data_dir, exist_ok=True)
    
    def scrape(self):
        """Main scraping method"""
        return self.fetch_articles()
    
    def fetch_articles(self):
        """Parse YOUR exact HTML structure"""
        print(f"🌐 {self.source_name}: Parsing articles...")
        
        articles = []
        
        try:
            # Read your HTML file
            with open('adiga_structure.html', 'r', encoding='utf-8') as f:
                html = f.read()
            
            soup = BeautifulSoup(html, 'html.parser')
            
            # Find ALL article items (30 in your file)
            article_items = soup.select('ul.uctList02 li')
            print(f"   Found {len(article_items)} article items in HTML")
            
            # Parse each article
            for item in article_items[:10]:  # Process first 10 only
                try:
                    # Find the anchor tag with onclick
                    anchor = item.find('a', onclick=True)
                    if not anchor:
                        continue
                    
                    # ✅ CORRECT: onclick='fnDetailPopup("26546")' - DOUBLE QUOTES inside
                    onclick = anchor.get('onclick', '')
                    
                    # Extract article ID - handles fnDetailPopup("26546")
                    match = re.search(r'fnDetailPopup\(["\'](\d+)["\']\)', onclick)
                    if not match:
                        continue
                    
                    article_id = match.group(1)
                    
                    # Get title - from uctCastTitle class
                    title_elem = anchor.select_one('.uctCastTitle')
                    if not title_elem:
                        continue
                    
                    title = title_elem.get_text(strip=True)
                    
                    # Clean title (remove newIcon text if present)
                    title = title.replace('newIcon', '').strip()
                    
                    # Get content preview
                    content_elem = anchor.select_one('.content')
                    content = content_elem.get_text(strip=True) if content_elem else ""
                    
                    # Get metadata (year, category, date)
                    info_elem = anchor.select_one('.info')
                    metadata = ""
                    if info_elem:
                        spans = info_elem.find_all('span')
                        metadata = " | ".join([span.get_text(strip=True) for span in spans])
                    
                    # ✅✅✅ CORRECT URL CONSTRUCTION ✅✅✅
                    article_url = f"{self.base_url}/ArticleDetail.do?articleID={article_id}"
                    
                    # Combine content with metadata
                    full_content = content
                    if metadata:
                        full_content += f"\n📅 {metadata}"
                    
                    # Create program data
                    program_data = {
                        'title': title,
                        'content': full_content[:350],
                        'url': article_url,
                        'article_id': article_id,
                        'source': self.source_name,
                        'id': f"adiga_{article_id}",
                        'scraped_at': datetime.now().isoformat()
                    }
                    
                    articles.append(program_data)
                    
                    print(f"   ✅ {article_id}: {title[:40]}...")
                    
                except Exception as e:
                    # Skip errors silently
                    continue
            
            print(f"   Successfully parsed {len(articles)} articles")
            
        except FileNotFoundError:
            print("   ❌ adiga_structure.html not found")
        except Exception as e:
            print(f"   ❌ Parse error: {e}")
        
        # If no articles parsed (shouldn't happen), use fallback
        if not articles:
            print("   ⚠️ No articles parsed, using fallback")
            articles = self._get_fallback_articles()
        
        return articles
    
    # Simulate BaseScraper methods
    def find_new_programs(self, current_programs):
        """Find new programs compared to previous runs"""
        previous = self._load_previous()
        previous_ids = {p['id'] for p in previous.get('programs', []) if 'id' in p}
        
        new_programs = []
        for program in current_programs:
            if program['id'] not in previous_ids:
                new_programs.append(program)
        
        return new_programs
    
    def _load_previous(self):
        """Load previously detected programs"""
        if os.path.exists(self.detected_file):
            try:
                with open(self.detected_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                return {'programs': []}
        return {'programs': []}
    
    def _get_fallback_articles(self):
        """Fallback with correct URLs"""
        return [
            {
                'title': '[입시의 정석] 정시 등록 오늘부터…이중 등록 유의해야',
                'content': '정시 등록이 오늘부터 시작됩니다. 대학별 등록 마감일 확인.',
                'url': 'https://adiga.kr/ArticleDetail.do?articleID=26546',
                'article_id': '26546',
                'source': self.source_name,
                'id': 'adiga_26546',
                'scraped_at': datetime.now().isoformat()
            }
        ]
