# KHCU Scraper Integration Guide

## ✅ Files Created

1. **`khcu_scraper.py`** - Complete scraper implementation
2. **`KHCU_STRUCTURE_ANALYSIS.md`** - Detailed HTML structure analysis
3. **Integration Instructions** (this file)

---

## 🚀 Integration Steps

### Step 1: Add Scraper to Your Project

Copy `khcu_scraper.py` to your scrapers directory:

```bash
cp khcu_scraper.py ~/uni_monitoring.kr/scrapers/
```

### Step 2: Update `config/sources.yaml`

Your current config already has KHCU defined. Verify it matches:

```yaml
sources:
  khcu:
    name: "Kyung Hee Cyber University"
    url: "https://khcu.ac.kr/schedule/index.do"
    enabled: true
    scraper_class: "KhcuScraper"
    scrape_interval: 1800
```

### Step 3: Update `config/filters.yaml`

Add or verify KHCU-specific department filters:

```yaml
departments:
  taxation_accounting:
    name: "세무회계학부"
    keywords: ['세무', '회계', '세무회계', 'taxation', 'accounting', 'tax']
    emoji: "💼"
    priority: 1
    enabled: true
    description: "Taxation & Accounting Department"
    
  finance_insurance:
    name: "금융보험학부"
    keywords: ['금융', '보험', '금융보험', 'finance', 'insurance', 'financial']
    emoji: "💰"
    priority: 2
    enabled: true
    description: "Finance & Insurance Department"
    
  business_admin:
    name: "경영학부"
    keywords: ['경영', '경영학', '경영관리', 'business', 'management', 'administration']
    emoji: "📊"
    priority: 3
    enabled: true
    description: "Business Administration Department"
```

### Step 4: Update `core/scraper_factory.py`

The factory should automatically register the scraper if it follows the naming convention. Verify:

```python
# The factory looks for:
# 1. File: scrapers/khcu_scraper.py
# 2. Class: KhcuScraper (ClassName pattern)
# 3. Config: scraper_class: "KhcuScraper" in sources.yaml

# If not auto-detected, manually add:
from scrapers.khcu_scraper import KhcuScraper

# In the factory's import section:
scrapers = {
    'KhcuScraper': KhcuScraper,
    # ... other scrapers
}
```

### Step 5: Test the Scraper

**Option A: Direct test (standalone)**

```bash
cd ~/uni_monitoring.kr
python3 scrapers/khcu_scraper.py
```

Expected output:
```
🧪 Testing KHCU Scraper
============================================================
Source name: khcu
Base URL: https://khcu.ac.kr

Testing connection...
✅ Connection successful

Testing scraping...

✅ Found XX schedule items:

1. 2026학년도 전기 입학식
   Date: 2026-02-28
   Department: None
   URL: https://khcu.ac.kr/schedule/index.do

2. 개강 및 강의 송출(12:00~)
   Date: 2026-03-02
   Department: None
   URL: https://khcu.ac.kr/schedule/index.do

... and more items

============================================================
✅ KHCU scraper test complete
```

**Option B: Integrated test via factory**

```bash
cd ~/uni_monitoring.kr
python3 core/monitor_engine.py --test --source khcu
```

**Option C: Full monitoring cycle**

```bash
python3 core/monitor_engine.py --verbose
```

---

## 📝 Expected Behavior

### What the Scraper Does:
1. ✅ Loads the KHCU schedule page using Selenium (JavaScript rendering)
2. ✅ Extracts all schedule items from the calendar
3. ✅ Parses dates from KHCU format (MM.DD(요일)) to YYYY-MM-DD
4. ✅ Filters items by department keywords (Taxation, Finance, Business)
5. ✅ Creates Article objects with all metadata
6. ✅ Handles errors gracefully with detailed logging

### What It Doesn't Do:
- ❌ **Not admission-focused**: This is an academic schedule page, not admission announcements
- ❌ **No department-specific announcements**: Schedule items are university-wide
- ❌ **Limited filtering**: Most items won't match department keywords
- ⚠️ **Requires active Selenium**: Headless Chrome must be installed

---

## 🔍 Expected Results

The KHCU scraper will find schedule items like:

```
Title: 2026학년도 전기 입학식
Date: 2026-02-28
Department: None (입학식 doesn't match department keywords)

Title: 2026-1학기 수강 신청 정정
Date: 2026-03-02 ~ 2026-03-09
Department: None (academic operation, not department-specific)

Title: 세무회계 과정 시작
Date: YYYY-MM-DD
Department: taxation_accounting (matches keyword '세무')
```

**Note**: Most items will have `department: None` because they're university-wide schedules, not department-specific announcements.

---

## 🛠️ Troubleshooting

### Issue: "ModuleNotFoundError: No module named 'selenium'"

```bash
pip install selenium
```

### Issue: "Chrome not found" or WebDriver error

```bash
# Install Chrome/Chromium
sudo apt-get install chromium-browser
# or
sudo apt-get install google-chrome-stable

# Or specify path if installed elsewhere
# Edit khcu_scraper.py and change:
driver = webdriver.Chrome(options=chrome_options)
# To:
driver = webdriver.Chrome('/path/to/chromedriver', options=chrome_options)
```

### Issue: No items found

1. Check if page loads: test browser manually
   ```bash
   google-chrome https://khcu.ac.kr/schedule/index.do
   ```

2. Verify CSS selectors haven't changed:
   ```bash
   python3 khcu_browser_explorer.py
   ```

3. Check logs for errors:
   ```bash
   grep -i "khcu\|error" logs/monitor.log
   ```

### Issue: Department detection not working

The filter is case-insensitive and substring-based. Verify keywords in `config/filters.yaml`:

```python
# Keywords should be lowercase in config
keywords: ['세무', '회계', 'taxation', 'accounting']

# All of these will match:
'세무회계학부' ✅
'2026-1학기 세무 관련 일정' ✅
'Taxation Process' ✅
'General Schedule' ❌
```

---

## 📊 Architecture Integration

The scraper integrates with your robust architecture:

```
config/sources.yaml
    ↓
core/scraper_factory.py (auto-loads based on scraper_class)
    ↓
scrapers/khcu_scraper.py (KhcuScraper class)
    ↓
core/monitor_engine.py (calls scraper.scrape())
    ↓
core/filter_engine.py (applies department filters)
    ↓
core/state_manager.py (duplicate detection via SQLite)
    ↓
notifiers/telegram_notifier.py (sends alerts)
```

---

## 🔄 Next Steps

1. **Test the scraper** (see Testing section above)
2. **Monitor logs** for any errors:
   ```bash
   tail -f logs/monitor.log | grep khcu
   ```
3. **Verify Telegram alerts** are being sent
4. **Consider adding admission-specific sources** if needed:
   - KHCU might have a separate admission portal
   - Check for admission announcement URLs

---

## 📌 Important Notes

### KHCU Content Type
- **What we're monitoring**: Academic calendar (학사일정)
- **What we're NOT monitoring**: Admission announcements
- **To monitor admissions**: Might need different URL or source

### Department Keywords
Your interests are:
- 세무회계 (Taxation & Accounting)
- 금융보험 (Finance & Insurance)  
- 경영학부 (Business Administration)

These are built into the scraper, but since KHCU schedule items are mostly university-wide, most items will be filtered out.

### Future Enhancement
If admission information is posted separately, you can:
1. Find the admission URL
2. Create a new source in `config/sources.yaml`
3. Create a new scraper following the same pattern
4. Update filters with admission keywords

---

## ✅ Validation Checklist

Before running with monitor_engine:

- [ ] `khcu_scraper.py` copied to `scrapers/`
- [ ] `config/sources.yaml` updated with KHCU config
- [ ] `config/filters.yaml` has department definitions
- [ ] Chrome/Chromium installed on system
- [ ] Selenium installed: `pip install selenium`
- [ ] `core/scraper_factory.py` can find KhcuScraper
- [ ] Test script runs without errors
- [ ] Can reach https://khcu.ac.kr in browser
- [ ] Telegram bot configured in `config/config.yaml`

---

**Status**: ✅ Ready for integration
**Next**: Run tests and activate in monitor_engine
