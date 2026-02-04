#!/usr/bin/env python3
"""
Adiga (어디가) scraper - Refactored to use filters.py
Based on original uni_monitor.py with standardized output format
"""
import requests
from bs4 import BeautifulSoup
import time
from datetime import datetime
import json
import os
import re
import sys
import hashlib

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scraper_base import BaseScraper
from sources import get_music_types, get_music_icons, get_music_names
from filters import analyze_title, should_keep_program, extract_university, TARGET_UNIVERSITIES

class AdigaScraper(BaseScraper):
    """Adiga scraper - uses centralized filters.py system"""
    
    # Original configuration from uni_monitor.py
    AJAX_URL = "https://www.adiga.kr/uct/nmg/enw/newsAjax.do"
    REFERER_URL = "https://www.adiga.kr/uct/nmg/enw/newsView.do?menuId=PCUCTNMG2000"
    
    def __init__(self, source_name, source_config):
        super().__init__(source_name, source_config)
        self.session = None
        
    # ========== ORIGINAL FUNCTIONS (preserved) ==========
    
    def extract_article_link(self, title_tag):
        """
        ORIGINAL FUNCTION: Extract direct article link WITH session context.
        """
        # Look for onclick with fnDetailPopup
        element = title_tag
        for _ in range(5):
            if element is None:
                break
            onclick = element.get('onclick', '')
            
            if 'fnDetailPopup' in onclick:
                # Extract article ID
                match = re.search(r"fnDetailPopup\('(\d+)'\)", onclick)
                if match:
                    article_id = match.group(1)
                    link = f"{self.REFERER_URL}&nttId={article_id}"
                    return link
            
            # Check parent element
            element = element.parent
        
        return self.REFERER_URL
    
    def send_telegram_alert(self, title, link, article_id, details):
        """
        ORIGINAL FUNCTION: Send Telegram alert (now handled by formatter)
        """
        # This is handled by TelegramFormatter in multi_monitor.py
        # Keeping for compatibility
        print(f"📨 Would send Telegram: {title[:50]}...")
        return True
    
    def fetch_adiga_articles(self):
        """
        ORIGINAL FUNCTION: Fetch articles from Adiga
        """
        if not self.session:
            self.session = requests.Session()
            self.session.headers.update({
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7',
                'Referer': self.REFERER_URL,
            })
        
        ajax_data = {
            'pageIndex': '1',
            'listType': 'list',
            'pageUnit': '50',
            'searchCnd': 'all',
            'searchWrd': '',
            'SITE_ID': 'uct',
            'bbsId': 'BBSMSTR_000000006421',
            'menuId': 'PCUCTNMG2000',
        }
        
        try:
            response = self.session.post(self.AJAX_URL, data=ajax_data, timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            articles = soup.find_all('tr', class_=lambda x: x and 'notice' not in x)
            
            return articles, soup, self.session
            
        except Exception as e:
            print(f"❌ Error fetching articles: {e}")
            return [], None, self.session
    
    def process_articles(self, articles, soup, session):
        """
        ORIGINAL FUNCTION: Process articles using centralized filters
        """
        new_postings = []
        
        for article in articles:
            # Find title element
            title_elem = article.find('td', class_='title')
            if not title_elem:
                continue
            
            title_tag = title_elem.find('a')
            if not title_tag:
                continue
            
            title = title_tag.get_text(strip=True)
            
            # Use centralized filter from filters.py
            should_keep, reason, analysis = should_keep_program(title)
            
            if not should_keep:
                # Optional: uncomment for debugging
                # print(f"  Filtered out: {reason}")
                continue
            
            # Extract university from analysis
            university = analysis['university']
            if not university:
                continue
            
            # Extract link
            link = self.extract_article_link(title_tag)
            
            # Extract article ID from link
            article_id = None
            if 'nttId=' in link:
                article_id = link.split('nttId=')[1].split('&')[0]
            
            # Create posting object
            posting = {
                'title': title,
                'link': link,
                'article_id': article_id,
                'university': university,
                'filter_analysis': analysis,  # Full analysis from filters.py
                'timestamp': datetime.now().isoformat(),
            }
            
            new_postings.append(posting)
        
        return new_postings
    
    # ========== NEW METHODS FOR STANDARDIZED FORMAT ==========
    
    def scrape(self):
        """
        NEW: Main scraping method that wraps original logic
        Returns standardized program data
        """
        print(f"🔍 {self.source_config.get('name', 'Adiga')}: Running...")
        
        # Use original functions
        articles, soup, session = self.fetch_adiga_articles()
        
        if not articles:
            print(f"   ℹ️ No articles found")
            return []
        
        # Process using original function
        raw_postings = self.process_articles(articles, soup, session)
        
        if not raw_postings:
            print(f"   ℹ️ No music admission articles found")
            return []
        
        print(f"   ✅ Found {len(raw_postings)} music admission articles")
        
        # Convert to standardized format
        programs = []
        for posting in raw_postings:
            program = self.normalize_program_data(posting)
            if program:
                programs.append(program)
        
        return programs
    
    def normalize_program_data(self, raw_posting):
        """
        Convert raw posting to standardized program format
        Uses filters.py analysis and sources.py for music classification
        """
        title = raw_posting.get('title', '')
        university = raw_posting.get('university', 'Unknown University')
        link = raw_posting.get('link', '')
        analysis = raw_posting.get('filter_analysis', {})
        
        # Get deadline from analysis
        deadline = analysis.get('deadline', '')
        
        # Use sources.py for music classification (consistent with filters)
        music_types = get_music_types(title)
        
        # Get region from university name
        from filters import get_region_for_university
        region = get_region_for_university(university)
        
        # Create program ID (consistent across runs)
        id_string = f"{university}_{title}_{deadline}"
        program_id = hashlib.md5(id_string.encode()).hexdigest()[:8]
        
        # Calculate days until deadline
        deadline_days = self._calculate_days_until(deadline)
        
        # Build standardized program object
        program = {
            'id': f"adiga_{program_id}",
            'source': 'adiga',
            'university': university,
            'department': analysis.get('department', '음악관련학과'),
            'program': title,
            'deadline': deadline,
            'deadline_parsed': self._parse_date(deadline),
            'deadline_days': deadline_days,
            'url': link,
            'music_types': music_types,
            'music_icons': get_music_icons(music_types),
            'music_names': get_music_names(music_types),
            'location': region,
            'urgency': analysis.get('urgency_level', 'normal'),
            'is_national': self._is_national_university(university),
            'scraped_at': datetime.now().isoformat(),
            'description': title[:100] + "..." if len(title) > 100 else title,
        }
        
        return program
    
    # ========== HELPER METHODS ==========
    
    def _parse_date(self, date_text):
        """Parse date string to datetime"""
        if not date_text:
            return None
        
        try:
            if '.' in date_text:
                parts = date_text.split('.')
                if len(parts) == 3:
                    year, month, day = map(int, parts)
                    return datetime(year, month, day)
        except Exception:
            pass
        
        return None
    
    def _calculate_days_until(self, deadline_text):
        """Calculate days until deadline"""
        deadline_date = self._parse_date(deadline_text)
        if not deadline_date:
            return None
        
        today = datetime.now()
        delta = (deadline_date - today).days
        return max(0, delta)  # Don't return negative days
    
    def _is_national_university(self, university):
        """Check if university is national/public"""
        national_keywords = [
            '국립대', '공립대', '서울대', '부산대', '경상국립대',
            '전남대', '전북대', '충남대', '강원대', '제주대'
        ]
        
        return any(keyword in university for keyword in national_keywords)

# ========== TEST FUNCTION ==========

def test_adiga_scraper():
    """Test the refactored Adiga scraper"""
    from sources import SOURCE_CONFIG
    
    print("🧪 Testing refactored Adiga scraper")
    print("=" * 60)
    
    scraper = AdigaScraper('adiga', SOURCE_CONFIG['adigo'])
    
    # Test scraping
    programs = scraper.scrape()
    
    if programs:
        print(f"\n✅ Found {len(programs)} programs")
        print("\n📋 Sample program (first 3):")
        for i, program in enumerate(programs[:3], 1):
            print(f"\n{i}. {program['university']}")
            print(f"   {program['music_icons']} {program['music_names']}")
            print(f"   전형: {program['program'][:50]}...")
            print(f"   마감: {program['deadline']} ({program['deadline_days']}일 후)")
            print(f"   지역: {program['location']}")
            print(f"   URL: {program['url'][:60]}...")
    else:
        print("❌ No programs found")
    
    return programs

if __name__ == "__main__":
    test_adiga_scraper()
