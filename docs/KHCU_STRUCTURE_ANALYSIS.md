# KHCU Website Structure Analysis

## 📋 Key Findings

### 1. **Page Structure**
- **URL**: `https://khcu.ac.kr/schedule/index.do`
- **Page Title**: 학사일정 > 학사안내 > 경희사이버대학교
- **Content Type**: Academic Calendar & Schedule
- **Rendering**: JavaScript-rendered (requires Selenium)

### 2. **Main Container**
```html
<div class="scheduleBox clearfix">
  <!-- Calendar view -->
  <div class="calendarW">...</div>
  
  <!-- Schedule list -->
  <div class="scheduleW">
    <ul class="scheduleList">
      <li>...</li>
      ...
    </ul>
  </div>
  
  <!-- Navigation buttons -->
  <div class="btnSchedule">
    <a class="btnPrev" href="?dateFilter=2026-1&page=1">이전</a>
    <a class="btnNext" href="?dateFilter=2026-3&page=1">다음</a>
  </div>
</div>
```

### 3. **Individual Schedule Item Structure**
```html
<li>
  <div class="txtSche">
    <span class="date">03.02(월)</span>
    <span>개강 및 강의 송출(12:00~)</span>
  </div>
</li>
```

### 4. **Schedule List Organization**
The page displays schedules organized by month:
- Each month has a `<div class="scheduleCont">`
- Month heading: `<h4 class="titSche">` with month number and English name
- Multiple schedule items within `<ul class="scheduleList">`

### 5. **Key CSS Selectors**
| Element | Selector | Purpose |
|---------|----------|---------|
| Main container | `.scheduleBox` | Top-level wrapper |
| Schedule list | `.scheduleList` | Contains all items for a month |
| Schedule item | `.scheduleList > li` | Individual schedule entry |
| Date | `.date` (within li) | Date in format MM.DD(요일) |
| Title/Content | `span` (second span in li) | Schedule description |
| Month container | `.scheduleCont` | Groups items by month |
| Month title | `.titSche` | Month header (h4) |

### 6. **Navigation Structure**
- **Year Tabs**: Located in `.tab > li > a` (href="?dateFilter=2026-1", etc.)
- **Current year**: 2026 (class="on")
- **Available years**: 2005-2026
- **Pagination**: Previous/Next buttons with `dateFilter` parameter

### 7. **Sample Announcements Found**
```
Date: 02.28(토)
Title: 2026학년도 전기 입학식

Date: 02.28(토)
Title: 2025학년도 전기 학위수여식

Date: 03.02(월)
Title: 개강 및 강의 송출(12:00~)

Date: 03.02(월) ~ 03.09(월)
Title: 2026-1학기 수강 신청 정정
```

### 8. **Data Extraction Pattern**
Each schedule item follows this structure:
```python
{
    'date': '02.28(토)',  # From span.date
    'title': '2026학년도 전기 입학식',  # From second span
    'url': 'https://khcu.ac.kr/schedule/index.do',  # No direct link (calendar view)
    'source': 'khcu',
    'published_date': None,  # Use parsed date instead
}
```

### 9. **Relevant Departments**
KHCU offers courses in many departments. Based on your interests:
- 세무회계학부 (Taxation & Accounting)
- 금융보험학부 (Finance & Insurance)
- 경영학부 (Business Administration)

**Keywords to filter**:
```python
taxation_accounting = ['세무', '회계', '세무회계', 'taxation', 'accounting']
finance_insurance = ['금융', '보험', 'finance', 'insurance']
business = ['경영', 'business', 'management']
```

### 10. **Important Notes**
- **No admission-specific links**: This is an academic calendar, not admission announcements
- **All items are schedule-based**: Shows class schedules, exam dates, deadlines, etc.
- **Date format**: MM.DD(요일) - needs parsing
- **Static content**: Once loaded, no AJAX required for each item
- **No department filter on page**: Must filter by keywords after extraction

---

## ⚠️ Considerations for Scraper

1. **Selenium Required**: Page uses JavaScript, needs browser rendering
2. **Date Parsing**: Format "MM.DD(요일)" → needs parsing for year context
3. **Content Type**: Academic calendar, NOT admission announcements
4. **Filtering Strategy**: Must match department keywords after extraction
5. **URL Strategy**: No direct links to items; all items point back to schedule/index.do
6. **Pagination**: Navigation via `?dateFilter=YYYY-M` parameters

---

## 🚀 Next Steps

1. Create `khcu_scraper.py` using:
   - Selenium for page rendering
   - BeautifulSoup for HTML parsing
   - CSS selectors: `.scheduleList > li`
   - Regex for date parsing
   - Filter engine for department matching

2. Implement methods:
   - `fetch_articles()` - Load page, extract all schedule items
   - `parse_article()` - Convert raw data to Article model
   - `detect_department()` - Match keywords for taxation, finance, business
   - `get_source_name()` - Return "khcu"

3. Handle:
   - Date parsing (MM.DD(요일) → YYYY-MM-DD)
   - Multi-month content extraction
   - Department filtering
   - Duplicate detection (same title across multiple views)
