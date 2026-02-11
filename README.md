# University Admission Monitoring System

## Overview

**uni_monitoring.kr** is an automated university admission monitoring system that tracks announcements and schedules from Korean universities. The system continuously monitors multiple sources, filters announcements by relevance, and sends notifications via Telegram to keep you informed about important admission-related information.

### Primary Monitoring Sources

1. **Adiga (어디가)** - University admission portal with centralized announcements  
   URL: https://www.adiga.kr

2. **Kyung Hee Cyber University (경희사이버대학교)** - Academic schedule and administrative announcements  
   URL: https://khcu.ac.kr/schedule/index.do

3. **Seoul Cyber University (서울사이버대학)** - Educational institution announcements via RSS feed  
   URL: https://www.iscu.ac.kr/rss.xml

The system is designed to be easily extended with additional university sources through configuration alone, without requiring code changes.

## 📅 Weekly Deadline Alerts (Wednesdays)

In addition to daily monitoring, the system sends a comprehensive weekly deadline report 
every Wednesday containing:

- **TOPIK exam schedules** - Registration dates, exam sitting dates, results announcements
- **University admission deadlines** - Spring/Fall recruitment windows  
- **Priority categorization** - Urgent (3 weeks), Upcoming (8 weeks), Future
- **Korea-only tracking** - All major Korean universities and institutions

This helps the target audience to plan ahead for exam registrations and application deadlines.

See `deadline_alerts.py` for configuration and deadline list.

---

## ⚡ Quick Start (5 minutes)

### 1. Clone the Repository

    git clone https://github.com/tantry/uni_monitoring.kr.git
    cd uni_monitoring.kr

### 2. Install Dependencies

    pip install -r requirements.txt

### 3. Configure Your Sources

Edit the configuration files to enable/disable sources:

    nano config/sources.yaml
    nano config/filters.yaml

### 4. Run a Test

Test the monitoring system:

    bash check_now.sh

Or test a specific source:

    python3 scrapers/khcu_scraper.py

### 5. Set Up Telegram Notifications (Optional)

Configure your Telegram bot in `config/config.yaml`:

```yaml
telegram:
  bot_token: "YOUR_BOT_TOKEN_HERE"
  chat_id: "YOUR_CHAT_ID_HERE"
```

### 6. Deploy as Scheduled Job

Run every 30 minutes via cron:

    */30 * * * * cd ~/uni_monitoring.kr && bash check_now.sh >> logs/cron.log 2>&1

---

## 🔧 Configuration Guide (30 minutes)

### Understanding config/sources.yaml

The `sources.yaml` file defines which universities to monitor. Each source has specific configuration options:

```yaml
sources:
  khcu:
    name: "Kyung Hee Cyber University"
    url: "https://khcu.ac.kr/schedule/index.do"
    enabled: true
    scraper_class: "khcu_scraper"
    scrape_interval: 1800
    
    # Advanced filtering options
    date_filter_days: 120              # Only items in next 4 months
    enable_department_filter: false    # See note below
    enable_item_type_filter: true      # Filter by type
    enable_exclude_filter: true        # Exclude holidays/expired
    confidence_threshold: 0.10         # 10% keyword match
```

### Configuration Options Explained

| Field | Purpose | Example |
|-------|---------|---------|
| `enabled` | Whether to monitor this source | `true` / `false` |
| `scraper_class` | Which scraper file to use | `"khcu_scraper"` |
| `scrape_interval` | Seconds between checks | `1800` (30 min) |
| `date_filter_days` | Limit items to N days ahead | `120` (4 months) |
| `enable_department_filter` | Filter by department keywords | `true` / `false` |
| `enable_item_type_filter` | Filter by item type | `true` / `false` |
| `enable_exclude_filter` | Exclude holidays/expired | `true` / `false` |
| `confidence_threshold` | Min keyword match % | `0.10` (10%) |

### Understanding config/filters.yaml

The `filters.yaml` file defines department keywords and filtering rules:

```yaml
global_confidence_threshold: 0.15

departments:
  taxation_accounting:
    keywords:
      - 세무          # Korean: Taxation
      - 회계          # Korean: Accounting
      - taxation      # English equivalent
      - accounting
    priority: 1
```

---

## 🏗️ Architecture Overview (Understanding the System)

### Two-Layer Filtering System

The system implements filtering at two levels:

**Layer 1: Scraper-Level Filtering** (config/sources.yaml)
- Applied BEFORE items enter the engine
- Configuration-driven via sources.yaml
- Per-source customization possible
- Uses confidence_threshold: 0.10 (10%)

**Layer 2: Engine-Level Filtering** (config/filters.yaml)
- Applied AFTER scraper returns items
- Global rule enforcement
- Department keyword matching
- Uses confidence_threshold: 0.15 (15%)

### Why Two Layers?

✅ **Flexibility**: Different sources can have different filter settings  
✅ **Performance**: Scraper-level filters reduce engine load  
✅ **Maintainability**: Clear separation of concerns  
✅ **Extensibility**: Easy to adjust per-source without code changes  

### How Confidence Threshold Works

Example: Department keyword matching

```
Article: "2026-1학기 세무회계학부 기말고사"
         ↓
Department keywords: [세무, 회계, 세무회계, taxation, accounting]
         ↓
Matches found: 세무, 회계, 세무회계 = 3 matches
         ↓
Confidence: 3/5 = 60%
         ↓
Threshold: 10% → 60% ≥ 10% ✅ MATCHED

Result: Article matches taxation_accounting department
```

---

## 📚 Key Discoveries from Development

### 1. Department Filtering

**Finding**: KHCU academic schedule is university-wide, NOT department-specific.

All items apply to all students:
- "2026-1학기 기말고사" (ALL students)
- "개강 안내" (ALL students)
- NO items mention specific departments (세무, 금융, 경영)

**Solution**: Disable department filter for KHCU, use item-type filter instead.

**Configuration**:
```yaml
khcu:
  enable_department_filter: false  # Won't work - no dept keywords
  enable_item_type_filter: true    # Admission/exam/registration items
```

### 2. Item Type Filtering

**What it filters**: Academic calendar items by category

**Item Types** (Korean → English):
- 입학 = Admission/Enrollment items
- 시험 = Exam/Test items  
- 등록 = Registration items

**Example Results**: KHCU returns ~76 items, filters to ~22 when using item-type filter

### 3. Date Range Filtering

**Purpose**: Limit results to items within N days

**Configuration**:
```yaml
date_filter_days: 120  # Only next 4 months (~120 days)
```

**Impact**: Removes old/expired items, focuses on upcoming dates

---

## 🔍 Troubleshooting

### No Telegram Alerts

1. **Check configuration**:
   ```bash
   cat config/config.yaml | grep -A 2 "telegram:"
   ```
   Verify `bot_token` and `chat_id` are set

2. **Check bot permissions**:
   - Ensure bot is admin in your Telegram channel
   - Bot must have message posting permissions

3. **Check logs**:
   ```bash
   tail -f logs/monitor.log | grep -i telegram
   ```

4. **Check if articles are found**:
   ```bash
   python3 scrapers/khcu_scraper.py
   ```
   Should show articles extracted

### No Articles Found

1. **Check scraper output**:
   ```bash
   python3 scrapers/khcu_scraper.py
   ```

2. **Check filter configuration**:
   - Verify department keywords match your content
   - Check if filters are too strict
   - Try disabling filters temporarily for testing

3. **Verify source URL**:
   ```bash
   curl -I https://khcu.ac.kr/schedule/index.do
   ```
   Should return HTTP 200

### YAML Configuration Errors

**Common error**: Missing colons or indentation

```bash
# Validate YAML syntax
python3 -c "import yaml; yaml.safe_load(open('config/sources.yaml'))"
```

Should output nothing (success) or show parse errors

---

## 📋 Project Structure

```
uni_monitoring.kr/
├── config/                    # Configuration management
│   ├── sources.yaml          # Source definitions (EDIT THIS)
│   ├── filters.yaml          # Department filters (EDIT THIS)
│   └── config.yaml           # Telegram config (EDIT THIS)
├── core/                      # Core business logic
│   ├── base_scraper.py       # Abstract base class
│   ├── monitor_engine.py     # Main monitoring orchestrator
│   ├── scraper_factory.py    # Dynamic scraper loading
│   ├── filter_engine.py      # Advanced filtering
│   └── state_manager.py      # Duplicate detection
├── scrapers/                  # Scraper implementations
│   ├── khcu_scraper.py       # KHCU academic schedule
│   ├── adiga_scraper.py      # Adiga admission portal
│   ├── rss_feed_scraper.py   # RSS feed parsing
│   └── scraper_template.py   # Template for new scrapers
├── models/                    # Data models
│   └── article.py            # Article data structure
├── notifiers/                 # Notification handlers
│   └── telegram_notifier.py   # Telegram integration
├── filters/                   # Filter implementations
│   └── department_filter.py   # Department keyword matching
├── data/                      # Data storage
│   └── state.db              # SQLite database (auto-created)
├── logs/                      # Log files
│   └── monitor.log           # Application logs
├── tests/                     # Test suite
├── utils/                     # Utility functions
├── scripts/                   # Utility scripts
├── multi_monitor.py          # Legacy monitoring script
├── check_now.sh              # Run monitoring once
├── push_to_github_safe.sh    # Safe GitHub push
└── README.md                 # This file
```

---

## 🚀 How to Add a New Source

### Step 1: Add to config/sources.yaml

```yaml
sources:
  new_university:
    name: "New University Name"
    url: "https://example.com/announcements"
    enabled: false             # Start disabled
    scraper_class: "new_university_scraper"
    scrape_interval: 1800
    confidence_threshold: 0.10
```

### Step 2: Create Scraper (if needed)

If using RSS or academic schedule format, you might reuse existing scrapers:

```yaml
scraper_class: "rss_feed_scraper"      # For RSS feeds
scraper_class: "khcu_scraper"          # For academic calendars
```

Otherwise, create new scraper from template:

```bash
cp scrapers/scraper_template.py scrapers/new_university_scraper.py
```

### Step 3: Implement Required Methods

In your new scraper:

```python
def fetch_articles(self) -> List[Dict]:
    """Fetch raw articles from source"""
    # Your implementation

def parse_article(self, raw_data: Dict) -> Article:
    """Parse raw data into Article model"""
    # Your implementation

def detect_department(self, article_data: Dict) -> Optional[str]:
    """Detect department from article"""
    # Return 'taxation_accounting', 'finance_insurance', etc.
```

### Step 4: Test Standalone

```bash
python3 scrapers/new_university_scraper.py
```

### Step 5: Enable and Deploy

```yaml
scraper_class: "new_university_scraper"
enabled: true  # Enable it
```

---

## 🎯 Adding Multiple URLs from Same Website

**Common Pattern**: One university may have multiple announcement locations

Example: KHCU has
- Academic calendar: https://khcu.ac.kr/schedule/index.do
- Admission news: https://khcu.ac.kr/admission/news.do
- Department notices: https://khcu.ac.kr/departments/notices.do

**Solutions**:

### Option 1: Multiple Source Entries (Recommended)

Create separate source entries:

```yaml
sources:
  khcu_schedule:
    name: "KHCU - Academic Schedule"
    url: "https://khcu.ac.kr/schedule/index.do"
    scraper_class: "khcu_scraper"
    
  khcu_admission:
    name: "KHCU - Admission News"
    url: "https://khcu.ac.kr/admission/news.do"
    scraper_class: "khcu_admission_scraper"
    
  khcu_departments:
    name: "KHCU - Department Notices"
    url: "https://khcu.ac.kr/departments/notices.do"
    scraper_class: "khcu_departments_scraper"
```

### Option 2: Multi-URL Scraper

Extend scraper to handle multiple URLs:

```python
class KhcuScraper(BaseScraper):
    def __init__(self, config: dict):
        super().__init__(config)
        self.urls = [
            "https://khcu.ac.kr/schedule/index.do",
            "https://khcu.ac.kr/admission/news.do"
        ]
    
    def fetch_articles(self) -> List[Dict]:
        articles = []
        for url in self.urls:
            articles.extend(self._fetch_from_url(url))
        return articles
```

---

## ✨ Features

* **Multi-Source Monitoring**: Monitors multiple Korean universities
* **Advanced Filtering**: Department keywords, item types, date ranges
* **Two-Layer Filtering**: Scraper-level + Engine-level for flexibility
* **Duplicate Detection**: SQLite database prevents repeated notifications
* **Real-Time Alerts**: Telegram notifications for new announcements
* **Configuration-Driven**: Add sources via YAML, no code changes
* **Modular Architecture**: Easy to extend with new sources
* **Robust Error Handling**: Comprehensive logging and fallbacks

---

## 🤖 Telegram Integration

### Enabling Notifications

1. Create bot via @BotFather on Telegram
2. Get your `BOT_TOKEN`
3. Create channel/group and get `CHAT_ID`
4. Update `config/config.yaml`:

```yaml
telegram:
  bot_token: "YOUR_TOKEN_HERE"
  chat_id: "YOUR_CHAT_ID_HERE"
```

### Message Format

The system sends formatted notifications:

```
🎵 [새 입학 공고] 경희사이버대학교

📌 항목: 입학식
📝 설명: 2026학년도 전기 입학식 안내
🔗 링크: https://khcu.ac.kr/schedule/index.do

#대학입시
```

---

## 🔄 GitHub Integration

### Safe Push System

The repository includes interactive push scripts:

```bash
# One-time setup
./setup_github_safe.sh

# Interactive push with review
./push_to_github_safe.sh

# Automatic push
./push_to_github.sh
```

All credentials are automatically excluded via `.gitignore`.

---

## 📊 System Status

### ✅ Completed & Working

- ✅ KHCU academic schedule monitoring (22 relevant items)
- ✅ Seoul Cyber University RSS feed
- ✅ Adiga admission portal
- ✅ Advanced multi-layer filtering
- ✅ Date range filtering
- ✅ Item-type filtering (admission/exam/registration)
- ✅ Telegram notifications
- ✅ Configuration management

### 🔄 In Progress

- 🔄 Adding more university sources
- 🔄 Expanding department keyword coverage

### 📋 Future Enhancements

- Web dashboard for monitoring status
- Email notifications as alternative to Telegram
- REST API for external integrations
- Machine learning for better filtering
- Mobile app push notifications

---

## 🐛 Common Issues & Solutions

### YAML Validation Errors

```bash
python3 -c "import yaml; yaml.safe_load(open('config/sources.yaml'))"
```

**Common issues**:
- Missing colons (should be `key: value`)
- Inconsistent indentation (use 2 spaces)
- Double-quotes in wrong places

### Filter Not Working

**Check if**:
- Department keywords match your content
- Confidence threshold is reasonable (0.10-0.15)
- Item type filter is enabled if department keywords missing

### No Items from KHCU

**Expected**: ~76 items total, ~22 after filtering

**If getting 0**: 
- Check if `enable_item_type_filter: true`
- Verify date range is not filtering everything
- Check logs for errors

---

## 📖 Documentation Reference

Additional documentation files:

- **NEXT_CHAT_SUMMARY.md** - Session context and discoveries
- **QUICK_REFERENCE_ADD_SOURCES.md** - Templates and checklists
- **REAL_ARCHITECTURE_EXPLAINED.md** - Deep architecture understanding
- **ADVANCED_FILTERING_GUIDE.md** - Detailed filter combinations

---

## 🤝 Contributing

### For New Scrapers

1. Copy `scraper_template.py`
2. Implement `fetch_articles()` and `parse_article()`
3. Add to `config/sources.yaml`
4. Test: `python3 scrapers/your_scraper.py`
5. Enable and deploy

### For Filter Adjustments

Edit `config/filters.yaml`:
- Add new department keywords
- Adjust confidence thresholds
- Update priorities

Changes take effect immediately (hot-reload).

---

## 📄 License

MIT License - see LICENSE file for details

---

**Last Updated**: February 11, 2026  
**Status**: ✅ Production Ready  
**Maintainer**: tantry  
**GitHub**: https://github.com/tantry/uni_monitoring.kr  

---

### 🎯 What's New in This Update

This README now includes insights from the latest development session:

✅ Explanation of two-layer filtering architecture  
✅ How confidence thresholds work  
✅ Key discoveries about KHCU academic schedule  
✅ Item-type filtering details  
✅ Examples of what each filter does  
✅ Troubleshooting section for common issues  
✅ How to add multiple URLs from same site  
✅ Updated configuration examples  
✅ Clear tiered structure (Quick Start → Config → Architecture → Troubleshooting)  
