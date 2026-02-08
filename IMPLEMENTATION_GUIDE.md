# ADIGA SCRAPER FIX - IMPLEMENTATION GUIDE

**Status**: Based on your diagnostic output, the scraper was fetching from the WRONG URL structure.

**Solution**: Point it to the actual notice board (`/cct/pbf/noticeList.do`) instead of the general news container (`/man/inf/mainView.do`).

---

## STEP 1: Update Configuration

**File**: `~/uni_monitoring.kr/config/sources.yaml`

```yaml
sources:
  adiga:
    name: "Adiga University Portal"
    url: "https://www.adiga.kr"
    enabled: true
    
    # CRITICAL CHANGE: Updated to use actual notice board
    announcement_paths:
      - path: "/cct/pbf/noticeList.do"
        menu_id: "PCCCTPBF1000"
        name: "공지사항 (Main Notices)"
        enabled: true
      
      - path: "/uct/nmg/enw/newsView.do"
        menu_id: "PCUCTNMG2000"
        name: "대입주요자료 (Admission News)"
        enabled: true
    
    # Selectors for extracting articles
    selectors:
      article_link: 'a[href*="prtlBbsId"]'
      content_area: '.board-view, .article-content, .content'
    
    # Quality validation
    quality_rules:
      min_content_length: 50
      reject_patterns:
        - "바로가기"
        - "퀵메뉴"
      accept_keywords:
        - "모집"
        - "공고"
        - "입학"
```

---

## STEP 2: Replace Scraper Implementation

**File**: `~/uni_monitoring.kr/scrapers/adiga_scraper.py`

Replace the entire file with the new version from `FIX_STEP_2_adiga_scraper.py`

**Key improvements:**
- Fetches from `/cct/pbf/noticeList.do` (actual announcement board)
- Looks for links with `prtlBbsId` parameter (real article IDs)
- Implements quality filtering to reject navigation text
- Validates content before sending to Telegram
- Detailed logging for debugging

---

## STEP 3: Test the Fixed Scraper

```bash
cd ~/uni_monitoring.kr

# Test just the scraper
python3 scrapers/adiga_scraper.py

# Expected output should show:
# - Articles with real titles (not "대학정보", "전형정보", etc.)
# - Non-zero content length
# - Proper filtering (fewer articles after quality checks)
```

---

## STEP 4: Verify with Monitor Engine

```bash
# Test mode (doesn't send Telegram)
python3 core/monitor_engine.py --test

# Check output:
# - Should fetch real announcements
# - Should filter out navigation items
# - Should show content in Telegram message preview
```

---

## STEP 5: Deploy to Production

```bash
# Run actual monitor with Telegram
python3 core/monitor_engine.py

# Check your Telegram channel for:
# - Real announcement titles (e.g., "서울대 음악학과 2026모집")
# - Meaningful content snippets
# - No navigation garbage
```

---

## ROOT CAUSE ANALYSIS

**Why was it broken?**

Your original scraper was fetching from:
```
https://www.adiga.kr/man/inf/mainView.do?menuId=PCMANINF1000
```

This URL returns a **container page** with section headers, not actual articles.

**What was in the 4 "articles":**
1. "대학정보" (University Info) - NAVIGATION HEADER
2. "전형정보" (Application Methods) - NAVIGATION HEADER
3. "학생부 종합전형 상담" - ADVISORY NOTICE
4. "표준공통 원서접수 가이드" - YOUTUBE LINK

**The fix:**
Changed to fetch from the **actual announcement board**:
```
https://www.adiga.kr/cct/pbf/noticeList.do?menuId=PCCCTPBF1000
```

This returns links with `prtlBbsId` parameters that point to **real announcement detail pages**.

---

## ROBUST ARCHITECTURE BENEFITS

This fix follows your robust architecture principles:

1. **Configuration-based**: URLs are in YAML, not hardcoded
2. **Modular**: Scraper logic is separate from configuration
3. **Scalable**: Easy to add new announcement boards (just add to YAML)
4. **Quality-controlled**: Multi-layer validation before Telegram
5. **Maintainable**: Clear quality rules for filtering
6. **Testable**: Each step can be tested independently

---

## IF THIS STILL DOESN'T WORK

If the fixed scraper still returns no articles or low-quality content:

1. **Check if the notice board has actual announcements:**
   ```bash
   curl -s "https://www.adiga.kr/cct/pbf/noticeList.do?menuId=PCCCTPBF1000" | grep -i "모집\|공고\|입학" | head -5
   ```

2. **The notice board might require additional parameters:**
   - Add pagination: `?menuId=PCCCTPBF1000&curPage=1`
   - Check for filtering: `?menuId=PCCCTPBF1000&searchKey=title&searchVal=모집`

3. **Alternative approach - Use different universities:**
   - Instead of relying on Adiga as aggregator
   - Scrape individual university sites directly
   - (See FUTURE_PROJECTS.md in PKB for this architecture)

---

## TROUBLESHOOTING

**Problem**: Scraper finds articles but still low quality

**Solution**: Adjust quality_rules in sources.yaml:
```yaml
quality_rules:
  accept_keywords:  # Add more keywords your announcements use
    - "모집"
    - "공고"
    - "입학"
    - "입시"        # ← Add this if announcements use it
    - "전형"        # ← Or this
    - "지원"        # ← Or this
```

**Problem**: No articles found at all

**Solution**: The notice board might have changed. Check:
```bash
# Find current notice board URL
curl -s "https://www.adiga.kr" | grep -o 'href="[^"]*"' | grep -i "notice\|공지"
```

**Problem**: Content still shows navigation text

**Solution**: Update reject_patterns:
```yaml
reject_patterns:
  - "바로가기"
  - "퀵메뉴"
  - "메뉴"           # ← More aggressive filtering
  - "본문바로가기"
  - "검색"
```

---

## IMPLEMENTATION CHECKLIST

- [ ] Update `config/sources.yaml` with new URLs
- [ ] Replace `scrapers/adiga_scraper.py` with fixed version
- [ ] Run `python3 scrapers/adiga_scraper.py` and verify output
- [ ] Run `python3 core/monitor_engine.py --test` and check preview
- [ ] Verify Telegram messages show real content (not navigation)
- [ ] If satisfied, run `python3 core/monitor_engine.py` for production

---

## NEXT PHASE (Future)

If Adiga continues to have issues, consider implementing individual university scrapers:
- 서울대학교 admission site
- 연세대학교 admission site
- 고려대학교 admission site
- See `FUTURE_PROJECTS.md` in PKB for full multi-university architecture

This would be MORE RELIABLE than depending on an aggregator site.

