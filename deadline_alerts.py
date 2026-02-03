from config import BOT_TOKEN, CHANNEL_ID
"""
UNIVERSITY DEADLINE TRACKER - ONE-SHOT
Runs on Wednesdays, sends weekly deadline report
"""
import requests
from datetime import datetime, timedelta
import time


DEADLINES = [
    ["Spring 2026 추가모집", "2026-02-10", "추가모집 공고 시작", 1, "추가모집"],
    ["Spring 2026 추가모집 마감", "2026-02-27", "Spring 추가모집 접수 마감", 1, "추가모집"],
    ["Fall 2026 정시모집 시작", "2026-04-01", "Fall 2026 정시모집 접수 시작", 1, "정시모집"],
    ["Fall 2026 정시모집 마감", "2026-05-15", "Fall 2026 정시모집 접수 마감", 1, "정시모집"],
    ["TOPIK 98회 접수", "2026-05-20", "TOPIK 98회 시험 접수 시작", 2, "TOPIK"],
    ["TOPIK 98회 시험일", "2026-07-12", "TOPIK 98회 시험", 2, "TOPIK"],
    ["Fall 2026 추가모집 시작", "2026-07-25", "Fall 2026 추가모집 공고 시작", 1, "추가모집"],
    ["Spring 2027 정시모집 시작", "2026-11-01", "Spring 2027 정시모집 접수 시작", 2, "정시모집"],
]

def calculate_days_remaining(target_date_str):
    try:
        today = datetime.now().date()
        target = datetime.strptime(target_date_str, "%Y-%m-%d").date()
        return (target - today).days
    except:
        return None

def categorize_deadlines():
    top_priority = []      # 0-21 days (3 weeks)
    medium_priority = []   # 22-56 days (4-8 weeks)
    future_deadlines = []  # 57+ days
    
    for name, date_str, desc, base_priority, category in DEADLINES:
        days_left = calculate_days_remaining(date_str)
        
        if days_left is None or days_left < 0:
            continue
        
        deadline_info = {
            'name': name,
            'date': date_str,
            'days': days_left,
            'desc': desc,
            'priority': base_priority,
            'category': category
        }
        
        if days_left <= 21:
            top_priority.append(deadline_info)
        elif days_left <= 56:
            medium_priority.append(deadline_info)
        else:
            future_deadlines.append(deadline_info)
    
    return top_priority, medium_priority, future_deadlines

def send_deadline_alert(message):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    data = {
        'chat_id': CHANNEL_ID,
        'text': message,
        'parse_mode': 'HTML',
        'disable_web_page_preview': True
    }
    
    try:
        response = requests.post(url, json=data, timeout=10)
        return response.status_code == 200
    except:
        return False

def generate_weekly_report():
    today = datetime.now()
    
    print(f"\n{'='*60}")
    print(f"DEADLINE CHECK - {today.strftime('%Y-%m-%d %H:%M')}")
    print(f"{'='*60}")
    
    top_priority, medium_priority, future = categorize_deadlines()
    
    message = f"📅 <b>대학 입시 마감일 알림</b> - {today.strftime('%Y년 %m월 %d일')}\n\n"
    
    if top_priority:
        message += "🔴 <b>긴급: 3주 이내 마감</b>\n"
        for item in sorted(top_priority, key=lambda x: x['days']):
            emoji = "⚠️" if item['days'] <= 7 else "⏰"
            message += f"{emoji} <b>{item['name']}</b>: {item['date']} (D-{item['days']})\n"
            message += f"   → {item['desc']}\n"
        message += "\n"
    
    if medium_priority:
        message += "🟡 <b>예정: 8주 이내 마감</b>\n"
        for item in sorted(medium_priority[:5], key=lambda x: x['days']):
            message += f"• {item['name']}: {item['date']} (D-{item['days']})\n"
        message += "\n"
    
    message += "🎯 <b>관심 대학 모니터링 중:</b>\n"
    message += "• 홍익대학교, 한양대학교, 강원대학교, 경상국립대학교\n"
    message += "• 전북대학교, 충남대학교 외 6개 국립대\n\n"
    
    if not top_priority and not medium_priority:
        message += "✅ 이번 주에 긴급 마감일이 없습니다.\n"
        next_deadline = min(future, key=lambda x: x['days']) if future else None
        if next_deadline:
            message += f"다음 주요 마감일: {next_deadline['name']} ({next_deadline['date']}, D-{next_deadline['days']})\n\n"
    
    total_upcoming = len(top_priority) + len(medium_priority)
    message += f"<i>📊 요약: 긴급 {len(top_priority)}건, 예정 {len(medium_priority)}건</i>\n\n"
    
    next_wednesday = today + timedelta(days=(2 - today.weekday()) % 7)
    message += f"---\n다음 알림: {next_wednesday.strftime('%m월 %d일')} 수요일"
    
    print(f"📊 Found: {len(top_priority)} urgent, {len(medium_priority)} upcoming deadlines")
    
    if send_deadline_alert(message):
        print("✅ Weekly report sent to Telegram")
        return True
    else:
        print("✗ Failed to send report")
        return False

if __name__ == "__main__":
    print("\n" + "="*60)
    print("📅 UNIVERSITY DEADLINE TRACKER")
    print("="*60)
    
    today = datetime.now()
    day_name = ["월", "화", "수", "목", "금", "토", "일"][today.weekday()]
    
    if today.weekday() == 2:  # Wednesday
        print(f"✅ Today is {day_name}요일 (Wednesday)")
        print("Running deadline check...")
        print("="*60)
        success = generate_weekly_report()
    else:
        print(f"⏸️  Today is {day_name}요일")
        print("Deadline check runs on Wednesdays only")
        print(f"Next check: 다음 수요일")
    
    print(f"\n✅ Complete at {datetime.now().strftime('%H:%M:%S')}")
    print("="*60)
