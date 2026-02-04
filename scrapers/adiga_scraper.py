#!/usr/bin/env python3
"""
Adiga (어디가) scraper - DEBUG FILTERING VERSION
Shows why articles are being filtered out
"""
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import os
import sys
import hashlib
import re

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from .scraper_base import BaseScraper
from sources import get_music_types, get_music_icons, get_music_names
from filters import should_keep_program, get_region_for_university, ADMISSION_KEYWORDS

# ===== ADD THIS DICTIONARY =====
DEPARTMENT_KEYWORDS = {
    'music': ['음악', '음악학과', '음악대학', '음악전공', '음악계열', '실용음악', '성악', '작곡'],
    'korean': ['한국어', '국어', '국어국문', '국문학', '한문', '한국언어', '언어문학'],
    'english': ['영어', '영어영문', '영문학', '영미어문', '영어교육', '영어학과'],
    'liberal': ['인문', '인문학', '교양', '교양교육', '기초교양', '자유학기', '자유전공']
}
# ===== END =====

class AdigaScraper(BaseScraper):
    """Adiga scraper - Shows filtering debug"""
    
    AJAX_URL = "https://www.adiga.kr/uct/nmg/enw/newsAjax.do"
    REFERER_URL = "https://www.adiga.kr/uct/nmg/enw/newsView.do?menuId=PCUCTNMG2000"
    
    def __init__(self, source_name, source_config):
        super().__init__(source_name, source_config)
        self.session = None
    
    def scrape(self):
        """Scraping with debug output"""
        print(f"🔍 {self.source_config.get('name', 'Adiga')}: Scraping...")
        
        real_programs = self._scrape_with_debug()
        
        if real_programs:
            print(f"\n✅ Found {len(real_programs)} REAL music admission programs!")
            return real_programs
        else:
            print(f"\n⚠️ No music admission programs found, using test data")
            return self._create_test_programs()
    
    def _scrape_with_debug(self):
        """Scrape with detailed debug output"""
        try:
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
            
            response = self.session.post(self.AJAX_URL, data=ajax_data, timeout=30)
            
            if response.status_code != 200:
                return []
            
            soup = BeautifulSoup(response.content, 'html.parser')
            list_container = soup.find('ul', class_='uctList02')
            
            if not list_container:
                return []
            
            list_items = list_container.find_all('li')
            print(f"   Found {len(list_items)} total articles")
            
            programs = []
            filtered_count = 0
            
            for i, item in enumerate(list_items[:20], 1):  # Check first 20
                try:
                    title_elem = item.find('p', class_='uctCastTitle')
                    if not title_elem:
                        continue
                    
                    title = title_elem.get_text(strip=True)
                    
                    # DEBUG: Show what keywords are found
                    title_lower = title.lower()
                    
		# Check department keywords
		dept_found = []
		for dept, keywords in DEPARTMENT_KEYWORDS.items():
    		for keyword in keywords:
        	if keyword in title_lower:
            dept_found.append(f"{dept}:{keyword}")
            break  # Found at least one keyword for this department

                    
                    # Check admission keywords  
                    admission_found = []
                    for keyword in ADMISSION_KEYWORDS:
                        if keyword in title_lower:
                            admission_found.append(keyword)
                    
                    # Apply filter
                    should_keep, reason, analysis = should_keep_program(title)
                    
                    if should_keep:
                        link = self._extract_link(item)
                        
                        program_data = {
                            'title': title,
                            'university': analysis.get('university', ''),
                            'department': analysis.get('department', '음악관련학과'),
                            'deadline': analysis.get('deadline', ''),
                            'url': link,
                            'analysis': analysis,
                        }
                        
                        program = self.normalize_program_data(program_data)
                        if program:
                            programs.append(program)
                            print(f"   ✓ KEPT: {title[:50]}...")
			print(f"     Department keywords: {dept_found}")
                            print(f"     Admission keywords: {admission_found}")
                    else:
                        filtered_count += 1
                        # Show why filtered (for first few)
                        if filtered_count <= 5:
                            print(f"   ✗ FILTERED [{i}]: {title[:50]}...")
                            print(f"     Reason: {reason}")
                            if music_found:
                                print(f"     Music keywords found: {music_found}")
                            if admission_found:
                                print(f"     Admission keywords found: {admission_found}")
                            
                except Exception as e:
                    continue
            
            print(f"\n   📊 Filtering summary:")
            print(f"   Total articles: {len(list_items)}")
            print(f"   Kept: {len(programs)}")
            print(f"   Filtered out: {filtered_count}")
            
            return programs
            
        except Exception as e:
            print(f"   ❌ Error: {e}")
            return []
    
    def _extract_link(self, item):
        """Extract article link"""
        try:
            link_elem = item.find('a', onclick=True)
            if link_elem:
                onclick = link_elem.get('onclick', '')
                match = re.search(r'fnDetailPopup\("(\d+)"\)', onclick)
                if match:
                    return f"{self.REFERER_URL}&nttId={match.group(1)}"
        except:
            pass
        
        return self.REFERER_URL
    
    def _create_test_programs(self):
        """Test programs"""
        test_data = [
            {
                'title': '홍익대학교 실용음악학과 재즈보컬 추가모집 (~2026.03.15)',
                'university': '홍익대학교',
                'department': '실용음악학과',
                'deadline': '2026.03.15',
                'url': 'https://www.adiga.kr/example1',
            },
        ]
        
        programs = []
        for test in test_data:
            program = self.normalize_program_data(test)
            if program:
                programs.append(program)
        
        return programs
    
    def normalize_program_data(self, raw_data):
        """Convert to standardized format"""
        title = raw_data.get('title', '')
        university = raw_data.get('university', 'Unknown')
        department = raw_data.get('department', '음악관련학과')
        deadline = raw_data.get('deadline', '')
        url = raw_data.get('url', '')
        
        music_types = get_music_types(title)
        region = get_region_for_university(university)
        
        id_string = f"{university}_{title}_{deadline}"
        program_id = hashlib.md5(id_string.encode()).hexdigest()[:8]
        
        # Calculate days
        deadline_days = None
        if deadline:
            try:
                if '.' in deadline:
                    parts = deadline.split('.')
                    if len(parts) == 3:
                        year, month, day = map(int, parts)
                        deadline_date = datetime(year, month, day)
                        today = datetime.now()
                        deadline_days = max(0, (deadline_date - today).days)
            except:
                pass
        
        # Urgency
        urgency = 'normal'
        if deadline_days is not None:
            if deadline_days <= 3:
                urgency = 'high'
            elif deadline_days <= 7:
                urgency = 'medium'
            elif deadline_days <= 14:
                urgency = 'low'
        
        # Build program
        program = {
            'id': f"adiga_{program_id}",
            'source': 'adiga',
            'university': university,
            'department': department,
            'program': title,
            'deadline': deadline,
            'deadline_days': deadline_days,
            'url': url,
            'music_types': music_types,
            'music_icons': get_music_icons(music_types),
            'music_names': get_music_names(music_types),
            'location': region,
            'urgency': urgency,
            'is_national': any(keyword in university for keyword in ['국립대', '서울대', '부산대']),
            'scraped_at': datetime.now().isoformat(),
            'description': title[:80] + "..." if len(title) > 80 else title,
        }
        
        return program

def test_adiga_scraper():
    """Test with debug"""
    from sources import SOURCE_CONFIG
    
    print("🧪 Adiga Scraper - FILTER DEBUG MODE")
    print("=" * 60)
    
    scraper = AdigaScraper('adiga', SOURCE_CONFIG['adigo'])
    programs = scraper.scrape()
    
    if programs:
        print(f"\n🎯 FINAL RESULT: {len(programs)} music admission programs")
        for i, program in enumerate(programs, 1):
            print(f"\n{i}. {program['university']}")
            print(f"   {program['music_icons']} {program['music_names']}")
            print(f"   {program['program'][:60]}...")
            if program['deadline']:
                print(f"   마감: {program['deadline']} ({program['deadline_days']}일 후)")
            print(f"   URL: {program['url'][:50]}...")
    else:
        print("\n❌ No music admission programs found in Adiga")
    
    return programs

if __name__ == "__main__":
    test_adiga_scraper()
