#!/usr/bin/env python3
"""
Adiga (어디가) scraper - MULTI-DEPARTMENT FILTERING VERSION
Shows why articles are being filtered out for all target departments
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

# ===== DEPARTMENT KEYWORDS =====
DEPARTMENT_KEYWORDS = {
    'music': ['음악', '음악학과', '음악대학', '음악전공', '음악계열', '실용음악', '성악', '작곡', '피아노', '바이올린'],
    'korean': ['한국어', '국어', '국어국문', '국문학', '한문', '한국언어', '언어문학', '국어교육'],
    'english': ['영어', '영어영문', '영문학', '영미어문', '영어교육', '영어학과', '영어전공'],
    'liberal': ['인문', '인문학', '교양', '교양교육', '기초교양', '자유학기', '자유전공', '기초과목']
}

ADMISSION_KEYWORDS = ADMISSION_KEYWORDS  # Already imported from filters

class AdigaScraper(BaseScraper):
    """Adiga scraper - Shows filtering debug for multiple departments"""
    
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
            print(f"\n✅ Found {len(real_programs)} department admission programs!")
            return real_programs
        else:
            print(f"\n⚠ No department admission programs found, using test data")
            return self._create_test_programs()
    
    def _scrape_with_debug(self):
        """Scrape with detailed debug output for all departments"""
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
            kept_count = 0
            
            for i, item in enumerate(list_items[:30], 1):  # Check first 30
                try:
                    title_elem = item.find('p', class_='uctCastTitle')
                    if not title_elem:
                        continue
                    
                    title = title_elem.get_text(strip=True)
                    
                    # DEBUG: Check keywords
                    title_lower = title.lower()
                    
                    # Check admission keywords
                    admission_found = []
                    for keyword in ADMISSION_KEYWORDS:
                        if keyword in title_lower:
                            admission_found.append(keyword)
                    
                    # Check department keywords
                    dept_found = []
                    departments_found = []
                    for dept, keywords in DEPARTMENT_KEYWORDS.items():
                        for keyword in keywords:
                            if keyword in title_lower:
                                dept_found.append(f"{dept}:{keyword}")
                                if dept not in departments_found:
                                    departments_found.append(dept)
                                break  # Found at least one keyword for this department
                    
                    # Use the filter module's should_keep_program for final decision
                    should_keep, reason, keywords, department = should_keep_program(title)
                    
                    if should_keep:
                        kept_count += 1
                        program_data = {
                            'title': title,
                            'link': self._extract_link(item),
                            'date': self._extract_date(item),
                            'department': department if department else (departments_found[0] if departments_found else 'general'),
                            'keywords': keywords,
                            'source': self.source_name,
                            'source_name': self.source_config.get('name', 'Adiga')
                        }
                        
                        program = self.normalize_program_data(program_data)
                        if program:
                            programs.append(program)
                            print(f"   ✓ KEPT [{kept_count}]: {title[:50]}...")
                            print(f"     Department: {program_data['department']}")
                            print(f"     Keywords: {', '.join(keywords[:3])}...")
                    else:
                        filtered_count += 1
                        print(f"   ✗ FILTERED [{i}]: {title[:50]}...")
                        print(f"     Reason: {reason}")
                        if admission_found:
                            print(f"     Admission keywords: {admission_found}")
                        if dept_found:
                            print(f"     Department keywords: {dept_found}")
                        
                except Exception as e:
                    print(f"   ⚠ Error processing item {i}: {e}")
                    continue
            
            print(f"\n   📊 Filtering summary:")
            print(f"   Total articles: {len(list_items[:30])}")
            print(f"   Kept: {kept_count}")
            print(f"   Filtered out: {filtered_count}")
            
            return programs
            
        except Exception as e:
            print(f"   ⚠ Scraping error: {e}")
            return []
    
    def _extract_link(self, item):
        """Extract article link"""
        link_elem = item.find('a')
        if link_elem and link_elem.get('href'):
            href = link_elem.get('href')
            if href.startswith('/'):
                return f"https://www.adiga.kr{href}"
            return href
        return ""
    
    def _extract_date(self, item):
        """Extract article date"""
        date_elem = item.find('span', class_='date')
        if date_elem:
            return date_elem.get_text(strip=True)
        return datetime.now().strftime('%Y-%m-%d')
    
    def _create_test_programs(self):
        """Create test programs for debugging"""
        test_programs = []
        
        test_data = [
            {
                'title': '[테스트] 서울대학교 음악학과 추가모집 공고',
                'link': 'https://example.com/test1',
                'date': '2024-12-20',
                'department': 'music',
                'keywords': ['music:음악', 'admission:추가모집'],
                'source': self.source_name,
                'source_name': self.source_config.get('name', 'Adiga')
            },
            {
                'title': '[테스트] 한양대학교 영어영문학과 모집안내',
                'link': 'https://example.com/test2',
                'date': '2024-12-25',
                'department': 'english',
                'keywords': ['english:영어', 'admission:모집'],
                'source': self.source_name,
                'source_name': self.source_config.get('name', 'Adiga')
            }
        ]
        
        for data in test_data:
            program = self.normalize_program_data(data)
            if program:
                test_programs.append(program)
        
        print(f"   ✅ Created {len(test_programs)} test programs")
        return test_programs
    
    def normalize_program_data(self, raw_data):
        """Normalize program data structure"""
        if not raw_data or 'title' not in raw_data:
            return None
        
        # Generate unique ID
        unique_string = f"{raw_data['title']}_{raw_data.get('link', '')}_{raw_data.get('date', '')}"
        program_id = hashlib.md5(unique_string.encode()).hexdigest()[:8]
        
        normalized = {
            'id': program_id,
            'title': raw_data['title'],
            'link': raw_data.get('link', ''),
            'date': raw_data.get('date', ''),
            'university': self._extract_university(raw_data['title']),
            'department': raw_data.get('department', ''),
            'keywords': raw_data.get('keywords', []),
            'source': raw_data.get('source', self.source_name),
            'source_name': raw_data.get('source_name', ''),
            'detected_at': datetime.now().isoformat()
        }
        
        return normalized
    
    def _extract_university(self, title):
        """Extract university name from title"""
        # Simple extraction - can be enhanced
        university_keywords = ['서울대', '한양대', '홍익대', '경희대', '성균관대', '고려대', '연세대']
        for uni in university_keywords:
            if uni in title:
                return f"{uni}학교"
        return ""


def test_adiga_scraper():
    """Test the Adiga scraper"""
    print("🧪 Testing Adiga Scraper")
    print("=" * 60)
    
    from sources import SOURCE_CONFIG
    
    scraper = AdigaScraper('adiga', SOURCE_CONFIG['adigo'])
    programs = scraper.scrape()
    
    print(f"\n📊 Total programs found: {len(programs)}")
    for i, program in enumerate(programs, 1):
        print(f"{i}. {program['title'][:50]}...")
        print(f"   Dept: {program.get('department', 'N/A')}")
        print(f"   Uni: {program.get('university', 'N/A')}")
    
    print("=" * 60)
    print("✅ Test complete")


if __name__ == "__main__":
    test_adiga_scraper()
