"""
Centralized filtering system for university admission monitoring
CORRECT VERSION - No recursive errors
"""
import re
from datetime import datetime

# ==================== TARGET CONFIGURATION ====================

TARGET_UNIVERSITIES = [
    "홍익대학교", "한양대학교", "강원대학교", "경상국립대학교",
    "강릉원주대학교", "상지대학교", "전북대학교", "충남대학교",
    "전남대학교", "제주대학교", "경기대학교", "가천대학교",
    "서울대학교", "부산대학교", "인하대학교",
    "경희대학교", "성균관대학교", "서울시립대학교",
]

UNIVERSITY_REGIONS = {
    '서울': ['홍익대학교', '한양대학교', '서울대학교', '경희대학교', 
            '성균관대학교', '서울시립대학교'],
    '경기': ['경기대학교', '가천대학교'],
    '강원': ['강원대학교', '강릉원주대학교'],
    '경남': ['경상국립대학교'],
    '전북': ['전북대학교'],
    '전남': ['전남대학교'],
    '충남': ['충남대학교'],
    '제주': ['제주대학교'],
    '부산': ['부산대학교'],
    '인천': ['인하대학교'],
    '기타': ['상지대학교'],
}

PREFERRED_REGIONS = ["서울", "경기", "인천", "강원"]

# ==================== KEYWORD CATEGORIES ====================

MUSIC_KEYWORDS = {
    'general': ["음악", "음악학과", "음악대학", "음악전공", "음악계열"],
    'applied': ["실용음악", "재즈", "재즈음악", "편곡", "음향", "미디", "실용음악과"],
    'classical': ["클래식", "성악", "오케스트라", "관현악", "피아노", "성악전공"],
    'vocal': ["보컬", "성악", "가창", "노래", "보컬재즈", "R&B", "알앤비"],
    'instrumental': ["기악", "악기", "피아노", "기타", "베이스", "드럼"],
    'theory': ["작곡", "이론", "음악이론", "편곡", "화성"],
}

ADMISSION_KEYWORDS = [
    "추가모집", "미충원", "정시 추가모집", "모집", "입학", "입시",
    "모집정원", "전형", "선발", "모집인원", "정원내", "정원외",
]

# ==================== HELPER FUNCTIONS ====================

def extract_university(text):
    """Extract university name from text"""
    for university in TARGET_UNIVERSITIES:
        if university in text:
            return university
    return None

def extract_department(text):
    """Extract department from title - NO RECURSION"""
    text_lower = text.lower()
    
    # Check for department patterns
    patterns = [
        r'(\w+대학\w*과)',      # 음악대학과
        r'(\w+학과)',           # 음악학과  
        r'(\w+전공)',           # 음악전공
        r'(\w+계열)',           # 음악계열
        r'(\w+부)',             # 음악부
    ]
    
    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            return match.group(1)
    
    # Check keywords directly (NO RECURSION)
    if any(keyword in text_lower for keyword in MUSIC_KEYWORDS['applied']):
        return "실용음악학과"
    elif any(keyword in text_lower for keyword in MUSIC_KEYWORDS['vocal']):
        return "성악전공"
    elif any(keyword in text_lower for keyword in MUSIC_KEYWORDS['classical']):
        return "음악학과"
    elif any(keyword in text_lower for keyword in MUSIC_KEYWORDS['general']):
        return "음악학과"
    
    return "음악관련학과"

def extract_deadline(text):
    """Extract deadline date - dynamic"""
    patterns = [
        (r'(\d{4})\.(\d{1,2})\.(\d{1,2})', 'full_date'),
        (r'(\d{4})-(\d{1,2})-(\d{1,2})', 'full_date'),
        (r'~(\d{1,2})\.(\d{1,2})', 'month_day'),
        (r'마감\s*[:：]\s*(\d{1,2})\.(\d{1,2})', 'month_day'),
    ]
    
    current_date = datetime.now()
    current_year = current_date.year
    current_month = current_date.month
    
    for pattern, pattern_type in patterns:
        match = re.search(pattern, text)
        if match:
            groups = match.groups()
            
            if pattern_type == 'full_date' and len(groups) == 3:
                year, month, day = map(int, groups)
                if year < current_year - 1:
                    year = current_year
                return f"{year}.{month:02d}.{day:02d}"
                
            elif pattern_type == 'month_day' and len(groups) == 2:
                month, day = map(int, groups)
                if month < current_month:
                    year = current_year + 1
                else:
                    year = current_year
                return f"{year}.{month:02d}.{day:02d}"
    
    return None

def calculate_urgency(deadline_text):
    """Calculate urgency based on current date"""
    if not deadline_text:
        return 'normal'
    
    try:
        if '.' in deadline_text:
            parts = deadline_text.split('.')
            if len(parts) == 3:
                year, month, day = map(int, parts)
                deadline_date = datetime(year, month, day)
                today = datetime.now()
                days_until = (deadline_date - today).days
                
                if days_until < -365:
                    return 'expired'
                elif days_until < 0:
                    return 'recent_past'
                elif days_until == 0:
                    return 'high'
                elif days_until <= 3:
                    return 'high'
                elif days_until <= 7:
                    return 'medium'
                elif days_until <= 30:
                    return 'low'
                else:
                    return 'normal'
    except:
        pass
    
    return 'normal'

# ==================== MAIN FILTER FUNCTIONS ====================

def analyze_title(title):
    """Analyze article title - NO RECURSION"""
    title_lower = title.lower()
    
    # Initialize result
    result = {
        'original_title': title,
        'is_music': False,
        'is_admission': False,
        'music_categories': [],
        'university': None,
        'deadline': None,
        'department': None,
        'urgency_level': 'normal',
    }
    
    # Check music keywords
    for category, keywords in MUSIC_KEYWORDS.items():
        for keyword in keywords:
            if keyword in title_lower:
                result['is_music'] = True
                if category not in result['music_categories']:
                    result['music_categories'].append(category)
    
    # Check admission keywords
    for keyword in ADMISSION_KEYWORDS:
        if keyword in title_lower:
            result['is_admission'] = True
            break
    
    # Extract other info
    result['university'] = extract_university(title)
    result['deadline'] = extract_deadline(title)
    result['department'] = extract_department(title)  # NO RECURSION HERE
    
    if result['deadline']:
        result['urgency_level'] = calculate_urgency(result['deadline'])
    
    return result
def should_keep_program(title, content=""):
    """
    Filter programs to keep admission announcements for multiple departments
    Returns: (should_keep, reason, keywords_found, department)
    """
    title_lower = title.lower()
    content_lower = content.lower() if content else ""
    full_text = title_lower + " " + content_lower
    
    # Check for admission keywords first
    admission_keywords_found = []
    for keyword in ADMISSION_KEYWORDS:
        if keyword in full_text:
            admission_keywords_found.append(keyword)
    
    if not admission_keywords_found:
        return False, "No admission keywords found", [], None
    
    # Define all department keywords
    DEPARTMENT_KEYWORDS = {
        'music': ['음악', 'music', '실기', '예술', '예체능', '피아노', '바이올린', '성악', '작곡'],
        'korean': ['한국어', '국어', 'korean', '한문', '국문', '언어', '문학'],
        'english': ['영어', 'english', '영문', '영미', '어학', '번역'],
        'liberal': ['자유', 'liberal', '인문', '교양', '인문학', '리버럴', '기초', '교과']
    }
    
    # Check which department(s) the program belongs to
    departments_found = []
    department_keywords_found = []
    
    for dept, keywords in DEPARTMENT_KEYWORDS.items():
        for keyword in keywords:
            if keyword in full_text:
                departments_found.append(dept)
                department_keywords_found.append(f"{dept}:{keyword}")
                break  # Found at least one keyword for this department
    
    if not departments_found:
        return False, "Not related to target departments", admission_keywords_found, None
    
    # Combine all keywords found
    all_keywords = department_keywords_found + admission_keywords_found
    
    # Determine primary department (take first found)
    primary_department = departments_found[0]
    
    return True, f"{primary_department.upper()} admission program found", all_keywords, primary_department

def get_region_for_university(university):
    """Get region for a university"""
    for region, universities in UNIVERSITY_REGIONS.items():
        if university in universities:
            return region
    return '기타'

def is_preferred_region(university):
    """Check if university is in preferred region"""
    region = get_region_for_university(university)
    return region in PREFERRED_REGIONS

def calculate_program_priority(analysis):
    """Calculate priority score"""
    score = 0
    
    urgency_scores = {
        'high': 30, 'medium': 20, 'low': 10, 'normal': 5,
        'recent_past': 2, 'expired': -100
    }
    score += urgency_scores.get(analysis.get('urgency_level', 'normal'), 0)
    
    university = analysis.get('university')
    if university and is_preferred_region(university):
        score += 15
    
    music_cats = analysis.get('music_categories', [])
    if 'applied' in music_cats:
        score += 10
    if 'vocal' in music_cats:
        score += 8
    
    if analysis.get('deadline'):
        score += 5
    
    return score

# ==================== TEST FUNCTION ====================

def test_filters():
    """Test the filter system"""
    current_date = datetime.now()
    print(f"🧪 Testing Filter System (Date: {current_date.strftime('%Y-%m-%d')})")
    print("=" * 60)
    
    test_cases = [
        "서울대학교 음악학과 추가모집 마감: 2024.12.20",
        "홍익대학교 실용음악학과 재즈보컬 전형 추가모집",
        "경기대학교 음악대학 성악전공 정시 추가모집 안내",
        "강원대학교 음악학과 추가모집 (~12.31)",
        "한양대학교 영어영문학과 모집안내",
        "부산대학교 공학과 입학안내",
        "인하대학교 실용음악과 모집 (~11.15)",
    ]
    
    for i, title in enumerate(test_cases, 1):
        print(f"\nTest {i}: {title}")
        should_keep, reason, analysis = should_keep_program(title)
        
        print(f"  Keep: {'✅' if should_keep else '❌'} ({reason})")
        print(f"  University: {analysis.get('university')}")
        print(f"  Music categories: {analysis.get('music_categories')}")
        print(f"  Deadline: {analysis.get('deadline')}")
        print(f"  Urgency: {analysis.get('urgency_level')}")
        
        if should_keep:
            priority = calculate_program_priority(analysis)
            region = get_region_for_university(analysis['university'])
            print(f"  Priority score: {priority}")
            print(f"  Region: {region}")
    
    print("\n" + "=" * 60)
    print("✅ Filter test complete")

# ==================== MAIN EXECUTION ====================

if __name__ == "__main__":
    test_filters()
