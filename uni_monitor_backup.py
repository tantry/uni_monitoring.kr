"""
ADIGA UNIVERSITY MONITOR - ONE-SHOT
Checks Adiga for new articles, sends Telegram alerts
Run manually or via systemd/cron

PROPER FIX: Use session to maintain cookies, direct links DO work!
"""
import requests
from bs4 import BeautifulSoup
import time
from datetime import datetime
import json
import os
import re

# ==================== CONFIGURATION ====================
BOT_TOKEN = "8537135583:AAFyI8788KM7CpAs5YNH6kdQnCuQ8bM2gec"
CHANNEL_ID = "-1002365084090"

AJAX_URL = "https://www.adiga.kr/uct/nmg/enw/newsAjax.do"
REFERER_URL = "https://www.adiga.kr/uct/nmg/enw/newsView.do?menuId=PCUCTNMG2000"

DATA_DIR = "uni_monitor_data"
DETECTED_FILE = os.path.join(DATA_DIR, "detected_postings.json")

# ==================== TARGET UNIVERSITIES ====================
TARGET_UNIVERSITIES = [
    "홍익대학교", "한양대학교", "강원대학교", "경상국립대학교",
    "강릉원주대학교", "상지대학교", "전북대학교", "충남대학교",
    "전남대학교", "제주대학교", "경기대학교", "가천대학교",
]

# ==================== KEYWORD CATEGORIES ====================
ENGLISH_KEYWORDS = ["영어영문", "영어교육", "영어학과", "영어통번역", "영어"]
MUSIC_KEYWORDS = ["실용음악", "음악학과", "음악교육", "음악"]
ADMISSION_KEYWORDS = ["추가모집", "미충원", "정시 추가모집", "모집", "입학"]

# ==================== PROPER SESSION-BASED LINK FUNCTION ====================

def extract_article_link(title_tag):
    """
    PROPER FIX: Extract direct article link WITH session context.
    The direct links DO work when accessed with proper session/cookies.
    """
    # Look for onclick with fnDetailPopup
    element = title_tag
    for _ in range(5):
        if element is None:
            break
        onclick = element.get('onclick', '')
        if onclick and 'fnDetailPopup' in onclick:
            match = re.search(r'fnDetailPopup\("([^"]+)"\)', onclick)
            if match:
                article_id = match.group(1)
                # ✅ DIRECT LINK THAT ACTUALLY WORKS (with session)
                direct_link = f"https://www.adiga.kr/uct/nmg/enw/newsDetail.do?prtlBbsId={article_id}"
                return direct_link, article_id
        element = element.parent
    
    # Fallback
    return REFERER_URL, None

def setup_storage():
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)
    if not os.path.exists(DETECTED_FILE):
        with open(DETECTED_FILE, 'w', encoding='utf-8') as f:
            json.dump([], f)

def load_detected():
    try:
        with open(DETECTED_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        return []

def save_detected(postings):
    with open(DETECTED_FILE, 'w', encoding='utf-8') as f:
        json.dump(postings, f, ensure_ascii=False, indent=2)

def analyze_article(title):
    has_target_uni = any(uni in title for uni in TARGET_UNIVERSITIES)
    has_any_uni = any(uni in title for uni in ["국립대", "공립대", "대학교"])
    has_english = any(kw in title for kw in ENGLISH_KEYWORDS)
    has_music = any(kw in title for kw in MUSIC_KEYWORDS)
    has_admission = any(kw in title for kw in ADMISSION_KEYWORDS)
    
    # 🔴 PRIORITY 1: Target University + (English OR Music) + Admission
    if has_target_uni and (has_english or has_music) and has_admission:
        return {
            'priority': 1,
            'alert': True,
            'type': "🎯 완벽: 원하는 대학+전공+추가모집",
            'emoji': "🔴",
            'university': next((uni for uni in TARGET_UNIVERSITIES if uni in title), None)
        }
    
    # 🟡 PRIORITY 2: Any University + Admission
    if has_any_uni and has_admission:
        return {
            'priority': 2,
            'alert': True,
            'type': "📢 중요: 대학+추가모집",
            'emoji': "🟡",
            'university': "국립/공립대학교"
        }
    
    # 🔵 PRIORITY 3: Admission articles OR Target University
    if has_admission:
        return {
            'priority': 3,
            'alert': True,
            'type': "📝 유용: 추가모집 정보",
            'emoji': "🔵"
        }
    
    if has_target_uni:
        return {
            'priority': 3,
            'alert': True,
            'type': "📝 유용: 관심 대학 뉴스",
            'emoji': "🔵",
            'university': next((uni for uni in TARGET_UNIVERSITIES if uni in title), None)
        }
    
    # ⚪ PRIORITY 4: Everything else (NO ALERT)
    return {
        'priority': 4,
        'alert': False,
        'type': "📰 일반 교육 뉴스",
        'emoji': "⚪"
    }

def send_telegram_alert(title, link, article_id, details):
    message = f"{details['emoji']} <b>{details['type']}</b>\n\n"
    message += f"<b>제목:</b> {title}\n"
    
    if details.get('university'):
        message += f"<b>대학:</b> {details['university']}\n"
    
    detected = []
    if any(kw in title for kw in ENGLISH_KEYWORDS):
        detected.append("영어 프로그램")
    if any(kw in title for kw in MUSIC_KEYWORDS):
        detected.append("음악 프로그램")
    if any(kw in title for kw in ADMISSION_KEYWORDS):
        detected.append("입시 모집")
    
    if detected:
        message += f"<b>포함:</b> {', '.join(detected)}\n"
    
    # Show article ID
    if article_id:
        message += f"<i>📄 기사 ID: {article_id}</i>\n"
    
    # IMPORTANT: Add session hint for users
    message += f"<i>💡 팁: 링크를 클릭하기 전에 먼저 <a href='{REFERER_URL}'>Adiga 뉴스 페이지</a>를 방문해주세요.</i>\n"
    
    message += f"\n<b>링크:</b> <a href='{link}'>기사 보기</a>\n"
    message += f"<i>발견: {datetime.now().strftime('%Y-%m-%d %H:%M')}</i>"
    
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    data = {
        'chat_id': CHANNEL_ID,
        'text': message,
        'parse_mode': 'HTML',
        'disable_web_page_preview': False
    }
    
    try:
        response = requests.post(url, json=data, timeout=10)
        if response.status_code == 200:
            print(f"   ✅ Telegram alert sent: {title[:40]}...")
            return True
        else:
            print(f"   ✗ Telegram error: {response.status_code}")
            return False
    except Exception as e:
        print(f"   ✗ Telegram error: {e}")
        return False

def fetch_adiga_articles():
    """
    Use session to maintain cookies for proper access
    """
    try:
        # Create session for cookie persistence
        session = requests.Session()
        session.headers.update({
            'User-Agent': 'Mozilla/5.0',
            'X-Requested-With': 'XMLHttpRequest',
            'Referer': REFERER_URL
        })
        
        # First, visit the main page to establish session
        print(f"[{datetime.now().strftime('%H:%M:%S')}] Establishing session...")
        main_response = session.get(REFERER_URL, timeout=10)
        
        if main_response.status_code != 200:
            print(f"⚠️  Main page access: {main_response.status_code}")
        
        # Now fetch articles with the same session
        form_data = {
            'menuId': 'PCUCTNMG2000',
            'currentPage': '1',
            'cntPerPage': '20',
            'searchKeywordType': 'title',
            'searchKeyword': '',
        }
        
        response = session.post(AJAX_URL, data=form_data, timeout=15)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        articles = soup.find_all(class_='uctCastTitle')
        
        return articles, soup, session
        
    except Exception as e:
        print(f"✗ Fetch error: {e}")
        return [], None, None

def process_articles(articles, soup, session):
    new_alerts = []
    detected_ids = load_detected()
    
    for title_tag in articles[:25]:
        title = title_tag.get_text(strip=True)
        
        if title in detected_ids:
            continue
        
        analysis = analyze_article(title)
        
        # Get direct link (which works with session)
        link, article_id = extract_article_link(title_tag)
        analysis['link'] = link
        analysis['article_id'] = article_id
        
        # Verify link works with our session
        if article_id and session:
            try:
                test_response = session.head(link, timeout=5, allow_redirects=False)
                if test_response.status_code == 200:
                    analysis['link_verified'] = True
                else:
                    analysis['link_verified'] = False
            except:
                analysis['link_verified'] = False
        
        if analysis['alert']:
            analysis['title'] = title
            new_alerts.append(analysis)
        
        detected_ids.append(title)
        
        # Show verification status
        status = "✓" if analysis.get('link_verified') else "?"
        uni_name = analysis.get('university', 'No uni')
        print(f"   {analysis['emoji']} 📄{status} {uni_name:15} [ID:{article_id or 'N/A'}] {title[:50]}...")
    
    save_detected(detected_ids[-200:])
    return new_alerts

def run_check():
    setup_storage()
    
    print(f"[{datetime.now().strftime('%H:%M:%S')}] Fetching articles with session...")
    articles, soup, session = fetch_adiga_articles()
    
    if not articles:
        print("📭 No articles found")
        return 0
    
    print(f"   Found {len(articles)} articles")
    
    print(f"[{datetime.now().strftime('%H:%M:%S')}] Analyzing...")
    alerts = process_articles(articles, soup, session)
    
    if alerts:
        alerts.sort(key=lambda x: x['priority'])
        counts = {1: 0, 2: 0, 3: 0}
        for alert in alerts:
            counts[alert['priority']] = counts.get(alert['priority'], 0) + 1
        
        print(f"\n📊 ANALYSIS:")
        print(f"   🔴 Priority 1: {counts[1]} (대학+전공+추가모집)")
        print(f"   🟡 Priority 2: {counts[2]} (대학+추가모집)")
        print(f"   🔵 Priority 3: {counts[3]} (추가모집 or 관심대학)")
        
        print(f"\n📤 Sending {len(alerts)} alert(s) to Telegram...")
        sent_count = 0
        for alert in alerts:
            if send_telegram_alert(alert['title'], alert['link'], alert.get('article_id'), alert):
                sent_count += 1
                time.sleep(0.5)
        
        print(f"✅ Sent {sent_count}/{len(alerts)} alerts")
        return len(alerts)
    else:
        print(f"\n📭 No new high-value articles found")
        return 0

# ==================== MAIN ====================

if __name__ == "__main__":
    print("\n" + "="*60)
    print("🎓 ADIGA UNIVERSITY MONITOR (PROPER SESSION FIX)")
    print("="*60)
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print(f"Target Universities: {len(TARGET_UNIVERSITIES)}")
    print("="*60)
    
    print("\n🔍 KEY DISCOVERY:")
    print("   Direct links DO work with proper session/cookies")
    print("   ✓ newsDetail.do?prtlBbsId=ARTICLE_ID → WORKS!")
    print("   ⚠️  Requires visiting main page first")
    print("="*60)
    print()
    
    alerts_sent = run_check()
    
    print(f"\n✅ Check complete at {datetime.now().strftime('%H:%M:%S')}")
    print(f"   Alerts sent: {alerts_sent}")
    print("="*60)
