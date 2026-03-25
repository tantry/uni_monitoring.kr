"""
UNIVERSITY DEADLINE TRACKER - ONE-SHOT
Runs on Wednesdays, sends weekly deadline report to Education & Training topic
"""
import yaml
import requests
from datetime import datetime, timedelta
import sys
import os

# Load config
with open('config/config.yaml', 'r') as f:
    config = yaml.safe_load(f)

BOT_TOKEN = config['telegram']['bot_token']
GROUP_ID = config['telegram']['group_id']

# Get topic ID for Education & Training (admissions)
TOPIC_ID = config['telegram']['topics'].get('admissions', None)

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
    top_priority = []
    medium_priority = []
    future_deadlines = []
    
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
        'chat_id': GROUP_ID,
        'text': message,
        'parse_mode': 'HTML',
        'disable_web_page_preview': True
    }
    
    if TOPIC_ID:
        data['message_thread_id'] = TOPIC_ID
    
    try:
        response = requests.post(url, json=data, timeout=10)
        return response.status_code == 200
    except Exception as e:
        print(f"Error sending: {e}")
        return False

def generate_weekly_report():
    today = datetime.now()
    
    print(f"\n{'='*60}")
    print(f"DEADLINE CHECK - {today.strftime('%Y-%m-%d %H:%M')}")
    print(f"{'='*60}")
    
    top, medium, future = categorize_deadlines()
    
    urgent_count = len(top)
    upcoming_count = len(medium)
    
    print(f"📊 Found: {urgent_count} urgent, {upcoming_count} upcoming deadlines")
    
    if urgent_count == 0 and upcoming_count == 0:
        print("No deadlines to report")
        return False
    
    today_str = today.strftime('%Y년 %m월 %d일')
    
    message = f"""📅 <b>주간 대입 일정</b> ({today_str} 수요일)

⚠️ <b>긴급 일정 (3주 이내)</b>
"""
    if top:
        for d in sorted(top, key=lambda x: x['days']):
            message += f"• {d['name']}: <b>{abs(d['days'])}일 후</b> ({d['date']})\n"
    else:
        message += "• 없음\n"
    
    message += f"""
📌 <b>예정 일정 (4-8주 이내)</b>
"""
    if medium:
        for d in sorted(medium, key=lambda x: x['days']):
            message += f"• {d['name']}: {d['days']}일 후 ({d['date']})\n"
    else:
        message += "• 없음\n"
    
    message += """
🔗 자세한 정보는 uni_monitoring.kr 참고

#대입일정 #마감임박"""
    
    return send_deadline_alert(message)

def test_mode():
    today = datetime.now()
    print(f"\n{'='*60}")
    print(f"TEST MODE - {today.strftime('%Y-%m-%d %H:%M')}")
    print(f"{'='*60}")
    
    top, medium, future = categorize_deadlines()
    
    urgent_count = len(top)
    upcoming_count = len(medium)
    
    print(f"📊 Found: {urgent_count} urgent, {upcoming_count} upcoming deadlines")
    
    if urgent_count == 0 and upcoming_count == 0:
        print("No deadlines to report")
        return
    
    print("\n📅 Would send:\n")
    
    today_str = today.strftime('%Y년 %m월 %d일')
    
    print(f"📅 <b>주간 대입 일정</b> ({today_str} 수요일)")
    print("\n⚠️ <b>긴급 일정 (3주 이내)</b>")
    for d in sorted(top, key=lambda x: x['days']):
        print(f"• {d['name']}: {abs(d['days'])}일 후 ({d['date']})")
    
    print("\n📌 <b>예정 일정 (4-8주 이내)</b>")
    for d in sorted(medium, key=lambda x: x['days']):
        print(f"• {d['name']}: {d['days']}일 후 ({d['date']})")
    
    print("\n🔗 #대입일정 #마감임박")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == '--test':
        test_mode()
    else:
        if generate_weekly_report():
            print("✅ Report sent to Education & Training topic")
        else:
            print("✗ Failed to send report")
