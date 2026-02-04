# University Admission Monitor System


```markdown
# University Admission Monitor System

A modular Python system for monitoring Korean university music program admissions, with Telegram alert notifications.

## 🎯 Current Status: WORKING SYSTEM

✅ **Complete modular architecture** with working Adiga scraper  
✅ **Centralized filtering system** for music program classification  
✅ **Telegram alert formatting** with source icons and music type icons  
✅ **Multi-source ready** - easily add Jinhaksa, Uway, etc.  
✅ **Dynamic date handling** - works for any year (2024, 2025, 2026, etc.)

## 📁 Project Structure

```
uni_monitoring.kr/
├── scrapers/                    # All scrapers inherit from BaseScraper
│   ├── adiga_scraper.py        # ✅ Working Adiga scraper
│   ├── scraper_base.py         # ✅ Base class for all scrapers
│   └── __init__.py             # ✅ Package marker
├── filters.py                   # ✅ Centralized filtering logic
├── sources.py                   # ✅ Source display configuration
├── telegram_formatter.py       # ✅ Telegram alert formatting
├── multi_monitor.py            # ✅ Main orchestrator
├── check_now.sh                # ✅ Shell script launcher
├── config.py                   # ✅ Configuration (BOT_TOKEN, CHAT_ID)
└── uni_monitor.py              # ⚠️ Old version (keep as backup)
```

## 🚀 Quick Start

1. **Clone repository**:
   ```bash
   git clone https://github.com/tantry/uni_monitoring.kr.git
   cd uni_monitoring.kr
   ```

2. **Configure Telegram** (edit `config.py`):
   ```python
   BOT_TOKEN = "your_telegram_bot_token"
   CHAT_ID = "your_chat_id"
   ```

3. **Run the monitor**:
   ```bash
   ./check_now.sh
   # or
   python3 multi_monitor.py
   ```

## 🔧 How It Works

### 1. **Scraping**
- Adiga scraper uses AJAX requests to `https://www.adiga.kr/uct/nmg/enw/newsAjax.do`
- Parses HTML with BeautifulSoup using correct selectors: `ul.uctList02 li`
- Extracts: title, link (from `fnDetailPopup`), date information

### 2. **Filtering**
Centralized in `filters.py`:
- **Music keywords**: 음악, 실용음악, 재즈, 보컬, 성악, etc.
- **Admission keywords**: 추가모집, 정시 추가모집, 모집, 입학, etc.
- **Target universities**: 홍익대학교, 한양대학교, 강원대학교, etc.
- **Date adjustment**: Automatically adjusts dates for current admission cycle

### 3. **Alert Formatting**
- Source icons: 📘 진학사, 📗 Uway, 📰 U뉴스, 📕 Adigo
- Music type icons: 🎻 클래식, 🎸 실용음악, 🎤 보컬전문, 🎹 기악
- Deadline urgency: 🔴 High (≤3 days), 🟡 Medium (≤7 days), 🟢 Low (≤14 days)

## 📊 Current Sources

| Source | Status | Coverage |
|--------|--------|----------|
| **Adiga (어디가)** | ✅ Working | General admission news (filters for music programs) |
| Jinhaksa (진학사) | 🚧 Planning | Need URL discovery |
| Uway (유웨이) | 🚧 Planning | Need implementation |
| U뉴스 (news.unn.net) | 🚧 Planning | Partially identified |

## 🚨 NEXT STEPS FOR NEW DEVELOPERS

### 1. **Improve Adiga Scraper Search**
The current Adiga scraper finds general admission news but needs better search parameters:

```python
# POTENTIAL IMPROVEMENTS:
# 1. Add search parameters to AJAX request:
ajax_data = {
    'pageIndex': '1',
    'listType': 'list',
    'pageUnit': '50',
    'searchCnd': 'title',  # Search in title only
    'searchWrd': '음악 추가모집',  # Music + supplementary
    'SITE_ID': 'uct',
    'bbsId': 'BBSMSTR_000000006421',
    'menuId': 'PCUCTNMG2000',
}

# 2. Try different endpoints:
# - https://www.adiga.kr/search.do?query=음악+추가모집
# - University-specific searches: "홍익대학교 음악 추가모집"

# 3. Search for specific parameters:
# - 특정 대학 (specific universities)
# - 음악 전공 (music majors)
# - 추가모집 기간 (supplementary admission period)
```

### 2. **Add Jinhaksa Scraper**
**URL Discovery Needed:**
```
POTENTIAL JINHAKSA URLS TO INVESTIGATE:
1. https://www.jinhak.com/Ent/Ent01/Ent0103.aspx  (Main admission page)
2. https://www.jinhak.com/Entrance/               (Entrance section)
3. https://www.jinhak.com/University/             (University info)
4. Search for: "음악 추가모집" on Jinhaksa site

INSPECTION METHOD:
1. Open browser DevTools (F12)
2. Go to Network tab
3. Search for music admissions on Jinhaksa
4. Find XHR/AJAX requests and copy:
   - Request URL
   - Form parameters
   - Response format
```

**Template for new scraper:**
```python
# scrapers/jinhaksa_scraper.py
class JinhaksaScraper(BaseScraper):
    def scrape(self):
        # TODO: Implement Jinhaksa-specific scraping
        # Should return standardized program format
        pass
```

### 3. **Add Uway Scraper**
**URL Discovery Needed:**
```
POTENTIAL UWAY URLS:
1. https://www.uway.com/Entrance/                 (Entrance info)
2. https://www.uway.com/University/               (University search)
3. Search function for "추가모집 음악"
```

### 4. **Exploration Script Template**
Create `explore_site.py` for new sites:
```python
def explore_site(url):
    """Discover site structure"""
    import requests
    from bs4 import BeautifulSoup
    
    response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
    soup = BeautifulSoup(response.content, 'html.parser')
    
    # Look for forms
    forms = soup.find_all('form')
    for form in forms:
        print(f"Form action: {form.get('action')}")
        print(f"Form method: {form.get('method')}")
    
    # Look for search-related elements
    search_inputs = soup.find_all('input', {'type': 'search', 'name': re.compile(r'search|query', re.I)})
    
    # Save HTML for manual inspection
    with open('site_exploration.html', 'w') as f:
        f.write(str(soup))
```

## 🔍 DEBUGGING TIPS

### 1. **Check Adiga Response:**
```bash
# Save and examine HTML response
python3 -c "
import requests
from bs4 import BeautifulSoup
url = 'https://www.adiga.kr/uct/nmg/enw/newsAjax.do'
data = {'pageIndex': '1', 'listType': 'list', 'pageUnit': '50'}
response = requests.post(url, data=data)
with open('debug.html', 'w') as f:
    f.write(response.text)
print('Saved to debug.html')
"
```

### 2. **Test Filters Independently:**
```bash
python3 filters.py  # Runs test cases
```

### 3. **Check Telegram Formatting:**
```bash
python3 telegram_formatter.py
```

## ⚙️ Configuration

### `config.py`
```python
# Telegram
BOT_TOKEN = "YOUR_BOT_TOKEN"          # From @BotFather
CHAT_ID = "YOUR_CHAT_ID"              # Channel/group chat ID

# Monitoring
CHECK_INTERVAL = 3600                 # Seconds between checks
```

### `filters.py` - Customize These Lists:
```python
# Target universities (modify as needed)
TARGET_UNIVERSITIES = [
    "홍익대학교", "한양대학교", "강원대학교",
    "경상국립대학교", "서울대학교", "경기대학교",
    # Add more here
]

# Music keywords (expand as needed)
MUSIC_KEYWORDS = {
    'applied': ["실용음악", "재즈", "편곡", "음향", "미디"],
    'classical': ["클래식", "성악", "오케스트라", "관현악"],
    'vocal': ["보컬", "성악", "가창", "노래", "R&B"],
}
```

## 🕐 Scheduling (Cron)

For automatic monitoring:
```bash
# Edit crontab
crontab -e

# Add line (runs every 6 hours):
0 */6 * * * cd /path/to/uni_monitoring.kr && ./check_now.sh

# Or more frequently during admission season:
0 */2 * * * cd /path/to/uni_monitoring.kr && ./check_now.sh
```

## 📈 Monitoring Results

The system saves detected programs in:
```
uni_monitor_data/
├── detected_adiga.json    # Adiga findings
├── detected_jinhaksa.json # Future Jinhaksa findings
└── detected_uway.json     # Future Uway findings
```

## 🐛 Common Issues & Solutions

1. **No articles found on Adiga:**
   - Check if Adiga website structure changed
   - Examine `debug_ajax_response.html` for current HTML
   - Update selectors in `adiga_scraper.py`

2. **Telegram not sending:**
   - Verify `BOT_TOKEN` and `CHAT_ID` in `config.py`
   - Check if bot has permission to send to channel
   - Test with `python3 multi_monitor.py` (shows alert in console)

3. **Dates wrong:**
   - System uses dynamic date adjustment
   - Past dates (2024) are adjusted to current year
   - Check `filters.py` `extract_deadline()` function

## 🤝 Contributing New Sources

To add a new source (e.g., Jinhaksa):

1. **Explore the site** to find admission listings
2. **Create scraper** in `scrapers/` following `BaseScraper` pattern
3. **Add source config** to `sources.py` `SOURCE_CONFIG`
4. **Test** with `python3 scrapers/new_scraper.py`
5. **Integrate** into `multi_monitor.py`

## 📞 Contact & Maintenance

This system is actively maintained. When starting new development sessions:

1. **Check current status** with `./check_now.sh`
2. **Review this README** for next steps
3. **Examine `git log`** for recent changes
4. **Test individual components** before making changes

---
**Last Updated**: 2026-02-04  
**System Status**: ✅ Operational (Adiga working, test data flow verified)  
**Next Priority**: Add Jinhaksa scraper after URL discovery
```

**END OF FILE - STOP COPYING HERE**

## **After pasting into nano:**

1. **Save**: `Ctrl+X` → `Y` → `Enter`
2. **Verify**:
   ```bash
   cd /path/to/uni_monitoring.kr
   wc -l README.md  # Should be ~250+ lines
   head -10 README.md  # Should show title
   ```
3. **Push to GitHub**:
   ```bash
   git add README.md
   git commit -m "Add comprehensive README with documentation"
   git push origin main
   ```

**Yes, copy everything from `# University Admission Monitor System` to the end, paste into nano, save.** That's exactly right!

**Last Updated**: 2026-02-04  
**System Status**: ✅ Operational  
**Next Priority**: Add Jinhaksa scraper
