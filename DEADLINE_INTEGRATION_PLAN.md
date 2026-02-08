# DEADLINE SYSTEM INTEGRATION PLAN

**Status**: The deadline_alerts.py system exists as a **separate, independent module** that runs on Wednesdays only.

**Current Implementation:**
```
deadline_alerts.py
├── Fixed DEADLINES list (hardcoded dates)
├── categorize_deadlines() - prioritizes by days remaining
├── generate_weekly_report() - formats Telegram message
└── Runs only on Wednesdays (day_of_week == 2)
```

**Key Properties:**
- **Source**: Hardcoded, not scraped (no web fetching)
- **Update frequency**: Weekly (Wednesday only)
- **Categories**: 3 priority levels
  - 🔴 TOP: 0-21 days (3 weeks)
  - 🟡 MEDIUM: 22-56 days (4-8 weeks)
  - 🟢 FUTURE: 57+ days
- **Notification**: Sends Telegram message with priorities
- **Integration**: Uses same Telegram bot as admission alerts

---

## CURRENT DEADLINES TRACKED

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

## INTEGRATION STRATEGY - ROBUST ARCHITECTURE

### Option A: Keep Separate (Current)
**Pros:**
- Works independently
- Doesn't affect admission scraper issues
- Simple to maintain

**Cons:**
- Duplicate Telegram notifications
- Can't share duplicate detection
- Different code structure

### Option B: Integrate into New Architecture (RECOMMENDED)

Integrate deadline_alerts as a **second content source** alongside admission announcements.

**Architecture:**
```
NEW UNIFIED SYSTEM:
├── core/monitor_engine.py
│   ├── AdmissionScraper (Adiga news)
│   ├── DeadlineSource (hardcoded dates)
│   └── NotificationPipeline (Telegram)
├── models/
│   └── Article (tracks both news AND deadlines)
├── config/
│   ├── sources.yaml (admission sources)
│   └── deadlines.yaml (deadline dates) ← NEW
└── notifiers/
    └── telegram_notifier.py (handles both)
```

---

## STEP 1: CREATE DEADLINE SOURCE CLASS

**File**: `~/uni_monitoring.kr/core/deadline_source.py`

```python
from typing import List, Dict, Any
from datetime import datetime, timedelta
import yaml

class DeadlineSource:
    """Treats deadlines like a content source - returns Article-like objects"""
    
    def __init__(self, config_path: str = "config/deadlines.yaml"):
        self.config = self._load_config(config_path)
        self.source_name = "deadline_tracker"
    
    def _load_config(self, config_path: str) -> dict:
        """Load deadlines from YAML configuration"""
        with open(config_path, 'r') as f:
            return yaml.safe_load(f)
    
    def fetch_articles(self) -> List[Dict[str, Any]]:
        """
        Return upcoming deadlines as 'articles'.
        This allows deadlines to use the same notification pipeline.
        """
        articles = []
        
        deadlines = self.config.get('deadlines', [])
        today = datetime.now().date()
        
        for deadline_item in deadlines:
            name = deadline_item['name']
            date_str = deadline_item['date']
            description = deadline_item['description']
            category = deadline_item.get('category', 'general')
            
            try:
                target_date = datetime.strptime(date_str, "%Y-%m-%d").date()
                days_left = (target_date - today).days
                
                # Skip past deadlines
                if days_left < 0:
                    continue
                
                # Create article-like object
                article = {
                    'title': f"[마감일] {name} (D-{days_left})",
                    'url': '',  # No URL for deadline
                    'content': f"{description}\n마감일: {date_str}",
                    'source': self.source_name,
                    'deadline': date_str,
                    'days_remaining': days_left,
                    'category': category,
                    'published_date': date_str,
                    'is_deadline': True,
                    'priority': self._calculate_priority(days_left)
                }
                
                articles.append(article)
            
            except Exception as e:
                print(f"Error processing deadline {name}: {e}")
                continue
        
        return articles
    
    def _calculate_priority(self, days_left: int) -> int:
        """Prioritize deadlines by urgency"""
        if days_left <= 7:
            return 1  # 🔴 URGENT (1 week)
        elif days_left <= 21:
            return 2  # 🟠 HIGH (3 weeks)
        elif days_left <= 56:
            return 3  # 🟡 MEDIUM (8 weeks)
        else:
            return 4  # 🟢 LOW (future)
    
    def parse_article(self, raw_data: Dict[str, Any]):
        """Convert deadline data to Article model"""
        from models.article import Article
        
        article = Article(
            title=raw_data.get('title', ''),
            url=raw_data.get('url', ''),
            content=raw_data.get('content', ''),
            source=self.source_name,
            deadline=raw_data.get('deadline'),
            published_date=raw_data.get('published_date'),
            metadata={
                'days_remaining': raw_data.get('days_remaining', 0),
                'category': raw_data.get('category', 'general'),
                'priority': raw_data.get('priority', 4),
                'is_deadline': True
            }
        )
        
        return article
    
    def get_source_name(self) -> str:
        return self.source_name
```

---

## STEP 2: CREATE DEADLINES CONFIG

**File**: `~/uni_monitoring.kr/config/deadlines.yaml`

```yaml
deadlines:
  # Spring 2026 Additional Recruitment
  - name: "Spring 2026 추가모집 공고"
    date: "2026-02-10"
    description: "Spring 2026 추가모집 공고 시작"
    category: "추가모집"
    base_priority: 1

  - name: "Spring 2026 추가모집 마감"
    date: "2026-02-27"
    description: "Spring 추가모집 접수 마감"
    category: "추가모집"
    base_priority: 1

  # Fall 2026 Regular Admission
  - name: "Fall 2026 정시모집 시작"
    date: "2026-04-01"
    description: "Fall 2026 정시모집 접수 시작"
    category: "정시모집"
    base_priority: 1

  - name: "Fall 2026 정시모집 마감"
    date: "2026-05-15"
    description: "Fall 2026 정시모집 접수 마감"
    category: "정시모집"
    base_priority: 1

  # TOPIK Exams
  - name: "TOPIK 98회 접수"
    date: "2026-05-20"
    description: "TOPIK 98회 시험 접수 시작"
    category: "TOPIK"
    base_priority: 2

  - name: "TOPIK 98회 시험일"
    date: "2026-07-12"
    description: "TOPIK 98회 시험"
    category: "TOPIK"
    base_priority: 2

  # Fall 2026 Additional Recruitment
  - name: "Fall 2026 추가모집 시작"
    date: "2026-07-25"
    description: "Fall 2026 추가모집 공고 시작"
    category: "추가모집"
    base_priority: 1

  # Spring 2027 Regular Admission
  - name: "Spring 2027 정시모집 시작"
    date: "2026-11-01"
    description: "Spring 2027 정시모집 접수 시작"
    category: "정시모집"
    base_priority: 2
```

---

## STEP 3: Update MonitorEngine to Include Deadlines

**File**: `~/uni_monitoring.kr/core/monitor_engine.py`

Add deadline source to the scraper factory:

```python
from core.deadline_source import DeadlineSource

class MonitorEngine:
    def __init__(self, config_path: str = "config/config.yaml"):
        # ... existing code ...
        self.sources = [
            AdigaScraper(config['sources']['adiga']),
            DeadlineSource(),  # ← ADD THIS
        ]
    
    def run(self):
        """Fetch from all sources (admission news + deadlines)"""
        all_articles = []
        
        for source in self.sources:
            print(f"\n📡 Fetching from {source.get_source_name()}...")
            
            articles = source.fetch_articles()
            print(f"   Found {len(articles)} items")
            
            for article in articles:
                parsed = source.parse_article(article)
                all_articles.append(parsed)
        
        # Filter and send to Telegram
        self.process_and_notify(all_articles)
```

---

## STEP 4: Update Notification Formatting

**File**: `~/uni_monitoring.kr/notifiers/telegram_notifier.py`

Add deadline-aware formatting:

```python
def format_message(self, article: Article) -> str:
    """Format article/deadline for Telegram"""
    
    # Check if this is a deadline
    if article.metadata.get('is_deadline'):
        priority = article.metadata.get('priority', 4)
        days = article.metadata.get('days_remaining', 0)
        
        # Different emoji based on urgency
        if priority == 1:
            emoji = "🔴"  # URGENT
            emoji_text = "<b>긴급: 7일 이내</b>"
        elif priority == 2:
            emoji = "🟠"  # HIGH
            emoji_text = "<b>주의: 3주 이내</b>"
        elif priority == 3:
            emoji = "🟡"  # MEDIUM
            emoji_text = "<b>예정: 2개월 이내</b>"
        else:
            emoji = "🟢"  # LOW
            emoji_text = "<b>향후: 2개월 이상</b>"
        
        message = f"{emoji} {emoji_text}\n\n"
        message += f"<b>마감일:</b> {article.deadline}\n"
        message += f"<b>내용:</b> {article.title}\n"
        message += f"\n{article.content}"
        
        return message
    
    else:
        # Regular admission article formatting
        # ... existing code ...
```

---

## STEP 5: Prevent Duplicate Deadline Notifications

**File**: `~/uni_monitoring.kr/core/monitor_engine.py`

Add deadline deduplication:

```python
def is_deadline_duplicate(self, deadline_date: str) -> bool:
    """Check if we already sent alert for this deadline"""
    conn = sqlite3.connect(self.db_path)
    cursor = conn.cursor()
    
    # Query by deadline date instead of content hash
    cursor.execute(
        'SELECT 1 FROM articles WHERE source=? AND deadline=?',
        ('deadline_tracker', deadline_date)
    )
    
    result = cursor.fetchone()
    conn.close()
    
    return result is not None
```

---

## MIGRATION PATH

### Phase 1 (Immediate): Keep Separate
- Don't change `deadline_alerts.py` yet
- Keep running separately on Wednesdays
- Fix the admission scraper first

### Phase 2 (After fixing admissions): Integrate
- Create `core/deadline_source.py`
- Add `config/deadlines.yaml`
- Update `core/monitor_engine.py` to include deadlines
- Disable old `deadline_alerts.py` (or use as cron job)

### Phase 3 (Polish): Unified System
- Single notification pipeline handles both
- Shared duplicate detection
- Unified Telegram formatting
- Single database for all content

---

## BENEFITS OF INTEGRATION

1. **Unified Notification Pipeline**: Same Telegram notifier for news and deadlines
2. **Shared Duplicate Detection**: Won't send same deadline alert twice
3. **Single Database**: All articles/deadlines tracked together
4. **Flexible Scheduling**: Run both on same schedule or separate
5. **Easier Maintenance**: All content sources in same architecture
6. **Better Filtering**: Can filter deadlines same as news (by department, etc.)

---

## RECOMMENDATION

**Before starting integration, fix the Adiga scraper first:**

1. ✅ Apply FIX_STEP_1 and FIX_STEP_2 (new URL + robust scraper)
2. ✅ Verify admission alerts work properly
3. ✅ Then integrate deadline system into new architecture

**Timeline:**
- Phase 1 (Now): Fix admission scraper
- Phase 2 (Next week): Create deadline_source.py and integrate
- Phase 3 (Following week): Unified notification pipeline

---

## IMPORTANT: DEADLINE DATA MAINTENANCE

The `DEADLINES` list is **manually maintained**. To add/update deadlines:

1. Edit `config/deadlines.yaml`
2. Add new deadline entry with format:
   ```yaml
   - name: "Event Name"
     date: "YYYY-MM-DD"
     description: "What's happening"
     category: "Category"
     base_priority: 1 or 2
   ```
3. Restart monitor - it will pick up changes

For **automatic deadline detection** (future), you could:
- Scrape university websites for "2026 모집일정" pages
- Parse PDF admission schedules
- Integrate with calendar APIs

But for now, manual YAML maintenance is simpler and more reliable.

