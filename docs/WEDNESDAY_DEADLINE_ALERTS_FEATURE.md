# Wednesday Deadline Alerts - Feature Documentation

## 📋 What It Does

**deadline_alerts.py** runs **ONLY on Wednesdays** and sends a comprehensive weekly deadline report to your Telegram channel. It tracks:

1. **University Admission Deadlines** (한국 대학만 / Korea Only)
   - Spring/Fall semester deadlines
   - Additional recruitment deadlines

2. **TOPIK Exam Schedules** (한국어능력시험)
   - Registration deadlines
   - Exam sitting dates
   - Results announcement dates

3. **Sitting Dates & Expected Announcements**
   - When exam dates are scheduled
   - When results will be announced
   - When next registration opens

---

## 🏗️ How It's Structured

### File Location
```
uni_monitoring.kr/
└── deadline_alerts.py
```

### Current Tracked Deadlines
```python
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
```

---

## 📊 How It Categorizes Deadlines

### Priority Levels (by urgency)

**🔴 High Priority: 0-21 days (3 weeks)**
```
Urgent deadlines that require immediate attention
Example: "⚠️ Spring 2026 추가모집 마감: 2026-02-27 (D-16)"
```

**🟡 Medium Priority: 22-56 days (4-8 weeks)**
```
Upcoming deadlines in next 2 months
Example: "• Fall 2026 정시모집 시작: 2026-04-01 (D-49)"
```

**🔵 Future Deadlines: 57+ days**
```
Long-term planning items
Example: "Spring 2027 정시모집 시작: 2026-11-01 (D-264)"
```

---

## 🔄 When It Runs

### Execution Rules
```python
if today.weekday() == 2:  # Wednesday only (Monday=0, Wednesday=2)
    generate_weekly_report()
```

**Wednesday Check:**
- Runs every Wednesday at scheduled time (via cron)
- Analyzes all deadlines for the upcoming week/month
- Sends comprehensive report to Telegram channel
- Report includes all categories with highlighted urgencies

---

## 📤 Output Format

### Telegram Message Example

```
📅 대학 입시 마감일 알림 - 2026년 02월 11일

🔴 긴급: 3주 이내 마감
⚠️ Spring 2026 추가모집 마감: 2026-02-27 (D-16)
   → Spring 추가모집 접수 마감

🟡 예정: 8주 이내 마감
• Fall 2026 정시모집 시작: 2026-04-01 (D-49)
• Fall 2026 정시모집 마감: 2026-05-15 (D-93)
• TOPIK 98회 접수: 2026-05-20 (D-98)

🎯 관심 대학 모니터링 중:
• 서울대학교, 연세대학교, 고려대학교
• 이화여자대학교, 성균관대학교, 한양대학교
• 홍익대학교, 한양대학교, 강원대학교, 경상국립대학교
• 전북대학교, 충남대학교 외 6개 국립대

📊 요약: 긴급 1건, 예정 5건

---
다음 알림: 02월 18일 수요일
```

---

## 🛠️ How to Run

### Manual Run
```bash
python3 deadline_alerts.py
```

### Scheduled via Cron (Every Wednesday)
```bash
0 9 * * 3 cd ~/uni_monitoring.kr && python3 deadline_alerts.py
```
(Runs at 9 AM every Wednesday)

---

## ➕ How to Add New Deadlines

### 1. Edit the DEADLINES list
```python
DEADLINES = [
    ["Event Name", "YYYY-MM-DD", "Description", priority, "Category"],
    # Example:
    ["TOPIK 99회 접수", "2026-08-15", "TOPIK 99회 시험 접수 시작", 2, "TOPIK"],
    ["TOPIK 99회 시험일", "2026-10-18", "TOPIK 99회 시험", 2, "TOPIK"],
]
```

### 2. Supported Categories
- `"추가모집"` - Additional recruitment
- `"정시모집"` - Regular recruitment  
- `"TOPIK"` - Korean language proficiency test
- Custom categories work too

### 3. Priority Levels
- `1` - University admission (higher urgency)
- `2` - TOPIK/exams (slightly lower urgency)
- Adjust based on your needs

---

## 🌍 Geographic Scope

**Current: Korea Only (한국 전역)**

Tracked locations:
- All Korean universities
- TOPIK exam dates in Korea
- Korean language proficiency testing centers

**Future Expansion Possible:**
- Africa locations (as mentioned)
- Other regions based on channel member needs
- Just add to DEADLINES list with location identifier

---

## 🔗 Integration with Main Monitor

### Dual Functionality
```
┌─────────────────────────────────────┐
│ check_now.sh (runs multiple times)  │
├─────────────────────────────────────┤
│ 1. Daily: Scrapes announcements     │ ← uni_monitor.py
│ 2. Wednesday: Sends deadline report │ ← deadline_alerts.py
└─────────────────────────────────────┘
```

### How They Work Together

**Daily Scraping** (uni_monitor.py):
- Runs every 30 minutes via cron
- Scrapes Adiga and other sources
- Sends alerts for NEW announcements
- Manages department filtering

**Weekly Summary** (deadline_alerts.py):
- Runs ONLY on Wednesdays
- Reviews all upcoming deadlines
- Sends comprehensive category-based report
- Helps with long-term planning

---

## 📝 Configuration

### Required Config
```yaml
# config/config.yaml or .env
telegram:
  bot_token: "YOUR_BOT_TOKEN"
  chat_id: "YOUR_CHANNEL_ID"
```

### Optional Customization
- Priority thresholds (days)
- University list to monitor
- Categories to track
- Report timing

---

## ✅ What's Tracked (Korea Only)

### University Deadlines
- Spring/Fall semester admissions
- Regular recruitment (정시모집)
- Additional recruitment (추가모집)
- Transfer enrollment deadlines

### TOPIK Exam Dates
- Registration opening/closing
- Exam sitting dates
- Results announcement dates
- Next cycle registration opens

### Key Universities Monitored
- Seoul National University (서울대학교)
- Yonsei University (연세대학교)
- Korea University (고려대학교)
- Ewha Womans University (이화여자대학교)
- Sungkyunkwan University (성균관대학교)
- Hanyang University (한양대학교)
- Hongik University (홍익대학교)
- Kangwon National University (강원대학교)
- Gyeongsang National University (경상국립대학교)
- Jeonbuk National University (전북대학교)
- Chungnam National University (충남대학교)
- And 6 other national universities

---

## 🚀 Feature Summary

| Feature | Status | Description |
|---------|--------|-------------|
| Wednesday-only alerts | ✅ Active | Runs every Wednesday at scheduled time |
| Deadline categorization | ✅ Active | 3-tier urgency system |
| TOPIK tracking | ✅ Active | Exam dates and registration windows |
| Korea-only scope | ✅ Current | All tracked deadlines in Korea |
| Telegram notifications | ✅ Active | Formatted weekly reports |
| Customizable deadlines | ✅ Available | Easy to add new deadlines |
| Geographic expansion | 📋 Planned | Africa and other regions in future |

---

## 📖 Related Documentation

See main README.md for:
- Daily scraping functionality (uni_monitor.py)
- General monitoring setup
- Telegram configuration
- Multi-source integration

---

**Status**: ✅ Active and Working  
**Last Updated**: February 11, 2026  
**Frequency**: Every Wednesday  
**Scope**: Korea Only (expandable)  
