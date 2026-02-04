#!/usr/bin/env python3
"""
Adiga (어디가) scraper - REFACTORED to match original uni_monitor.py structure
Preserves all original functions and logic
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

class AdigaScraper(BaseScraper):
    """Adiga scraper - preserves original uni_monitor.py functions"""
    
    # Original configuration from uni_monitor.py
    AJAX_URL = "https://www.adiga.kr/uct/nmg/enw/newsAjax.do"
    REFERER_URL = "https://www.adiga.kr/uct/nmg/enw/newsView.do?menuId=PCUCTNMG2000"
    
    # Target universities (from original config)
    TARGET_UNIVERSITIES = [
        "홍익대학교", "한양대학교", "강원대학교", "경상국립대학교",
        "강릉원주대학교", "상지대학교", "전북대학교", "충남대학교", 
        "전남대학교", "제주대학교", "경기대학교", "가천대학교",
    ]
    
    # Keyword categories (from original)
    ENGLISH_KEYWORDS = ["영어영문", "영어교육", "영어학과", "영어통번역", "영어"]
    KOREAN_KEYWORDS = ["한국어", "한국어학과", "한국어교육", "한국어문학", "한글", "한국언어"]
    MUSIC_KEYWORDS = ["실용음악", "음악학과", "음악교육", "음악"]
    ADMISSION_KEYWORDS = ["추가모집", "미충원", "정시 추가모집", "모집", "입학"]
    
    def __init__(self, source_name, source_config):
        super().__init__(source_name, source_config)
        self.session = None
        
    # ========== ORIGINAL FUNCTIONS (preserved) ==========
    
    def extract_article_link(self, title_tag):
        """
        ORIGINAL FUNCTION: Extract direct article link WITH session context.
        The direct links DO work when accessed with proper session/cookies.
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
    
    def analyze_article(self, title):
        """
        ORIGINAL FUNCTION: Analyze article title for relevant keywords
        """
        details = {
            'is_english': False,
            'is_korean': False,
            'is_music': False,
            'is_admission': False,
            'university': None,
            'music_type': None,
        }
        
        title_lower = title.lower()
        
        # Check language programs
        for keyword in self.ENGLISH_KEYWORDS:
            if keyword in title_lower:
                details['is_english'] = True
                break
        
        for keyword in self.KOREAN_KEYWORDS:
            if keyword in title_lower:
                details['is_korean'] = True
                break
        
        # Check music programs
        for keyword in self.MUSIC_KEYWORDS:
            if keyword in title_lower:
                details['is_music'] = True
                
                # Determine music type
                if '실용음악' in title_lower:
                    details['music_type'] = 'applied'
                elif '음악' in title_lower:
                    details['music_type'] = 'classical'
                break
        
        # Check admission type
        for keyword in self.ADMISSION_KEYWORDS:
            if keyword in title_lower:
                details['is_admission'] = True
                break
        
        # Extract university
        for university in self.TARGET_UNIVERSITIES:
            if university in title:
                details['university'] = university
                break
        
        return details
    
    def send_telegram_alert(self, title, link, article_id, details):
        """
        ORIGINAL FUNCTION: Send Telegram alert (will be replaced by formatter)
        """
        # This will be handled by the TelegramFormatter in multi_monitor.py
        # Keeping function signature for compatibility
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
        ORIGINAL FUNCTION: Process articles and check for new ones
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
            
            # Analyze article
            details = self.analyze_article(title)
            
            # We only care about music admissions
            if not details['is_music'] or not details['is_admission']:
                continue
            
            # Extract university
            university = details['university']
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
                'details': details,
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
        """
        title = raw_posting.get('title', '')
        university = raw_posting.get('university', 'Unknown University')
        link = raw_posting.get('link', '')
        details = raw_posting.get('details', {})
        
        # Extract more info from title
        deadline = self._extract_deadline(title)
        
        # Detect music types using sources.py
        music_types = get_music_types(title)
        
        # Extract region
        region = self._extract_region(university)
        
        # Create unique ID
        id_string = f"{university}_{title}_{link}"
        program_id = hashlib.md5(id_string.encode()).hexdigest()[:8]
        
        # Build standardized program
        program = {
            'id': f"adiga_{program_id}",
            'source': 'adiga',
            'university': university,
            'department': self._extract_department(title),
            'program': title,
            'deadline': deadline,
            'deadline_parsed': self._parse_date(deadline),
            'deadline_days': self._calculate_days_until(deadline),
            'url': link,
            'music_types': music_types,
            'music_icons': get_music_icons(music_types),
            'music_names': get_music_names(music_types),
            'location': region,
            'urgency': self._calculate_urgency(deadline),
            'is_national': self._is_national_university(university),
            'scraped_at': datetime.now().isoformat(),
            'description': title[:100] + "..." if len(title) > 100 else title,
            'original_details': details,  # Keep original analysis
        }
        
        return program
    
    # ========== HELPER METHODS ==========
    
    def _extract_deadline(self, text):
        """Extract deadline from text"""
        patterns = [
            r'(\d{4})\.(\d{1,2})\.(\d{1,2})',  # 2024.12.31
            r'(\d{4})-(\d{1,2})-(\d{1,2})',    # 2024-12-31
            r'~(\d{1,2})\.(\d{1,2})',          # ~12.31
            r'마감\s*:\s*(\d{1,2})\.(\d{1,2})', # 마감: 12.31
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                if pattern.startswith('~'):
                    return f"~{match.group(1)}.{match.group(2)}"
                elif '마감' in pattern:
                    return f"{match.group(1)}.{match.group(2)}"
                elif len(match.groups()) == 3:
                    return f"{match.group(1)}.{match.group(2)}.{match.group(3)}"
                elif len(match.groups()) == 2:
                    # Assume current year
                    current_year = datetime.now().year
                    return f"{current_year}.{match.group(1)}.{match.group(2)}"
        
        return ""
    
    def _extract_department(self, text):
        """Extract department from title"""
        patterns = [
            r'(\w+대학\w*과)',      # 음악대학과
            r'(\w+학과)',           # 음악학과
            r'(\w+전공)',           # 음악전공
            r'(\w+계열)',           # 음악계열
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                return match.group(1)
        
        return "음악관련학과"
    
    def _extract_region(self, university):
        """Extract region from university name"""
        region_map = {
            '서울': '서울', '연세': '서울', '고려': '서울', '성균관': '서울',
            '한양': '서울', '서울시립': '서울', '홍익': '서울',
            '경기': '경기', '수원': '경기', '가천': '경기',
            '인하': '인천', '인천': '인천',
            '강원': '강원', '강릉': '강원',
            '부산': '부산', '경상': '진주', '전북': '전북',
            '전남': '광주', '충남': '대전', '제주': '제주'
        }
        
        for key, region in region_map.items():
            if key in university:
                return region
        
        return '기타'
    
    def _parse_date(self, date_text):
        """Parse date string to datetime"""
        if not date_text:
            return None
        
        try:
            # Remove ~ prefix if present
            clean_text = date_text.replace('~', '').strip()
            
            formats = ['%Y.%m.%d', '%Y-%m-%d', '%m.%d']
            
            for fmt in formats:
                try:
                    if fmt == '%m.%d':
                        current_year = datetime.now().year
                        full_date = f"{current_year}.{clean_text}"
                        return datetime.strptime(full_date, '%Y.%m.%d')
                    return datetime.strptime(clean_text, fmt)
                except ValueError:
                    continue
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
        return max(0, delta)
    
    def _calculate_urgency(self, deadline_text):
        """Calculate urgency based on days until deadline"""
        days = self._calculate_days_until(deadline_text)
        
        if days is None:
            return 'normal'
        elif days <= 3:
            return 'high'
        elif days <= 7:
            return 'medium'
        elif days <= 14:
            return 'low'
        else:
            return 'normal'
    
    def _is_national_university(self, university):
        """Check if university is national/public"""
        national_keywords = [
            '국립대', '공립대', '서울대', '부산대', '경상국립대',
            '전남대', '전북대', '충남대', '강원대', '제주대'
        ]
        
        return any(keyword in university for keyword in national_keywords)

# ========== ORIGINAL RUN_CHECK FUNCTION (adapted) ==========

def run_check():
    """
    Adapted from original run_check() function
    Now integrated into multi_monitor.py
    """
    print("🚀 Adiga University Monitor")
    print("=" * 40)
    
    from sources import SOURCE_CONFIG
    
    scraper = AdigaScraper('adiga', SOURCE_CONFIG['adigo'])
    
    # Run scraper
    programs = scraper.scrape()
    
    if not programs:
        print("❌ No programs found")
        return []
    
    print(f"\n✅ Found {len(programs)} programs")
    
    # Find new programs
    new_programs = scraper.find_new_programs(programs)
    
    if new_programs:
        print(f"🎯 New programs detected: {len(new_programs)}")
        # Save current state
        scraper.save_detected(programs)
    else:
        print("🔁 No new programs")
    
    return new_programs

# ========== TEST FUNCTION ==========

def test_refactored_scraper():
    """Test the refactored scraper"""
    print("🧪 Testing refactored Adiga scraper (original logic preserved)")
    print("=" * 60)
    
    from sources import SOURCE_CONFIG
    
    scraper = AdigaScraper('adiga', SOURCE_CONFIG['adigo'])
    
    # Test 1: Check original functions exist
    print("\n1. Checking original functions:")
    funcs = ['extract_article_link', 'analyze_article', 'fetch_adiga_articles', 
             'process_articles', 'send_telegram_alert']
    
    for func in funcs:
        if hasattr(scraper, func):
            print(f"   ✅ {func}() exists")
        else:
            print(f"   ❌ {func}() missing")
    
    # Test 2: Run scraping
    print("\n2. Running scrape():")
    programs = scraper.scrape()
    
    if programs:
        print(f"   ✅ Found {len(programs)} programs")
        print(f"\n3. Sample program format:")
        program = programs[0]
        print(f"   ID: {program.get('id')}")
        print(f"   University: {program.get('university')}")
        print(f"   Music: {program.get('music_icons')} {program.get('music_names')}")
        print(f"   Deadline: {program.get('deadline')}")
        print(f"   URL: {program.get('url')[:60]}...")
    else:
        print("   ⚠️ No programs found (might be normal if no current announcements)")
    
    print("\n" + "=" * 60)
    print("✅ Refactored scraper test complete")
    
    return programs

if __name__ == "__main__":
    # Run the test
    test_refactored_scraper()
