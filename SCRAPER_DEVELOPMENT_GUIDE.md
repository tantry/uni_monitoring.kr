# Scraper Development Guide

## 🎯 Purpose
This guide captures critical lessons learned from developing scrapers for Korean university admission sites. Use this checklist when creating new scrapers to avoid common pitfalls.

---

## 📋 Pre-Development Checklist

### Step 1: Identify the Website Type

Visit the target website manually and answer these questions:

#### 1.1 Cookie/Consent Requirements
- [ ] Does a cookie consent popup appear on first visit?
- [ ] Is content blocked until consent is given?
- **Solution**: Implement cookie acceptance in Selenium (see example below)

#### 1.2 JavaScript Rendering
- [ ] Right-click → View Page Source: Is the HTML minimal (< 1000 bytes)?
- [ ] Does the page source show actual content or just JavaScript loaders?
- [ ] Do article links use `onclick` handlers instead of `href`?
- **Solution**: Use Selenium instead of requests/BeautifulSoup

#### 1.3 Link Behavior Pattern
Test by clicking an article link manually:

**Pattern A: Direct Navigation**
- URL changes to article page (e.g., `/article/12345`)
- Content loads on new page
- **Solution**: Simple HTTP requests work

**Pattern B: JavaScript Popups/Modals**
- URL stays the same or changes to `#none`
- Content appears in popup/overlay on same page
- Functions like `fnDetailPopup()`, `openModal()` in onclick
- **Solution**: Use Selenium to click links and extract popup content

**Pattern C: POST Requests**
- Links trigger POST requests instead of GET
- Check browser DevTools → Network tab when clicking
- **Solution**: Selenium or replicate POST request with requests.post()

**Pattern D: Search/Filter Required**
- Link goes to search page requiring user selection
- No direct article URLs available
- **Solution**: Selenium automation of search process

#### 1.4 Authentication/Session Requirements
- [ ] Does the site require login?
- [ ] Are articles behind a paywall?
- [ ] Does content require active session cookies?
- **Solution**: Session management or Selenium cookie handling

---

## 🔧 Implementation Patterns

### Pattern 1: Simple HTTP Scraper (Rare for Korean Sites)

**When to use**: Static HTML, direct links, no JavaScript
```python
def fetch_articles(self):
    response = requests.get(self.base_url)
    soup = BeautifulSoup(response.content, 'html.parser')
    # Parse directly
```

### Pattern 2: Selenium for JavaScript Rendering

**When to use**: JavaScript-rendered content, dynamic loading
```python
def _init_selenium(self):
    options = Options()
    options.add_argument('--headless=new')
    options.add_argument('--no-sandbox')
    options.binary_location = '/usr/bin/google-chrome-beta'
    
    service = Service('/usr/bin/chromedriver')
    self.driver = webdriver.Chrome(service=service, options=options)
```

### Pattern 3: Cookie Acceptance (Common for Korean Sites)

**When to use**: Cookie consent popups block content
```python
def _accept_cookies(self):
    self.driver.get("https://example.com")
    time.sleep(2)
    
    # Look for consent buttons
    cookie_selectors = [
        "//button[contains(text(), '동의')]",
        "//button[contains(text(), '확인')]",
        "//button[contains(text(), '모두 동의')]",
    ]
    
    for selector in cookie_selectors:
        try:
            button = WebDriverWait(self.driver, 3).until(
                EC.element_to_be_clickable((By.XPATH, selector))
            )
            button.click()
            return True
        except:
            continue
```

### Pattern 4: Clicking Popup Links (Adiga Pattern)

**When to use**: Articles open in popups, not new pages
```python
def fetch_articles(self):
    # Find all popup links
    popup_links = self.driver.find_elements(
        By.XPATH, 
        "//a[contains(@onclick, 'fnDetailPopup')]"
    )
    
    for link in popup_links:
        # Extract article ID from onclick
        onclick = link.get_attribute('onclick')
        match = re.search(r'fnDetailPopup\s*\(\s*["\'](\d+)["\']\s*\)', onclick)
        article_id = match.group(1)
        
        # Click to open popup
        self.driver.execute_script("arguments[0].click();", link)
        time.sleep(2)
        
        # Extract content from popup
        page_source = self.driver.page_source
        soup = BeautifulSoup(page_source, 'html.parser')
        
        # Find popup content
        popup = soup.find('div', class_='popCont')
        content = popup.get_text(strip=True) if popup else ""
        
        # Close popup
        try:
            close_btn = self.driver.find_element(
                By.XPATH, 
                "//button[contains(@class, 'close')]"
            )
            close_btn.click()
        except:
            pass
```

---

## 🧪 Testing Checklist

Before considering a scraper complete:

- [ ] **Step 1**: Run scraper and verify it finds articles (count > 0)
- [ ] **Step 2**: Check article titles are meaningful (not navigation text)
- [ ] **Step 3**: Visit 3 article URLs manually - do they work?
- [ ] **Step 4**: Check article content length (should be > 50 chars)
- [ ] **Step 5**: Verify content is actual article text, not error messages
- [ ] **Step 6**: Test with monitor_engine.py integration
- [ ] **Step 7**: Verify Telegram notifications work (if configured)

---

## 🚨 Common Failure Patterns

### Symptom: Finding 0 articles
**Causes**:
1. JavaScript not rendered → Use Selenium
2. Cookies not accepted → Implement cookie handling
3. Wrong URL or page structure changed

### Symptom: Finding navigation links instead of articles
**Causes**:
1. Filtering keywords too broad
2. Not distinguishing between menu items and articles
3. Wrong CSS selectors

**Fix**: Add skip terms:
```python
skip_terms = ['로그인', '회원가입', '검색', '사이트맵', '메뉴', '홈으로']
if any(term in text for term in skip_terms):
    continue
```

### Symptom: Article URLs return errors or blank pages
**Causes**:
1. URLs are JavaScript popups, not real pages (Adiga pattern)
2. Session/cookie required
3. POST request needed instead of GET

**Fix**: Use Selenium to click links instead of constructing URLs

### Symptom: Content is empty or just the title
**Causes**:
1. Popup content not extracted correctly
2. Content is dynamically loaded after page load
3. Wrong CSS selectors for content

**Fix**: 
- Add wait time after clicking: `time.sleep(2)`
- Try multiple selectors for popup content
- Check page_source after clicking to see what appeared

---

## 📚 Adiga Case Study

**Problem Discovery Process**:
1. Initial scraper found 77 links, but only 8 seemed admission-related
2. Those 8 were navigation menu items, not articles
3. Visiting constructed URLs showed errors/blank pages
4. **Key Discovery**: Articles use `fnDetailPopup()` which opens popups
5. **Solution**: Click links with Selenium, extract popup content

**Critical Lessons**:
- Never assume `href` URLs work - test them manually first
- Check `onclick` attributes for JavaScript functions
- Korean sites often use popups instead of separate pages
- Cookie consent is nearly universal on Korean sites

**Working Solution**:
```python
# 1. Initialize Selenium with proper Chrome/ChromeDriver versions
# 2. Accept cookies on homepage first
# 3. Navigate to news page
# 4. Find links with onclick="fnDetailPopup(...)"
# 5. Click each link with Selenium
# 6. Extract content from popup that appears
# 7. Close popup before clicking next link
```

---

## 🔄 Updating This Guide

When you encounter a new pattern or solve a difficult scraping problem:

1. Add it to this guide under appropriate section
2. Include code example
3. Note which site exhibited the pattern
4. Update scraper_template.py if pattern is common

**This is a living document - keep it updated!**

---

## 📝 Quick Reference

| Site Characteristic | Detection Method | Solution |
|-------------------|------------------|----------|
| Cookie consent | Popup on first visit | Selenium cookie acceptance |
| JavaScript rendering | View source shows minimal HTML | Use Selenium |
| Popup articles | onclick with function calls | Click links with Selenium |
| POST requests | DevTools Network tab | requests.post() or Selenium |
| Session required | Content blocked without login | Session/cookie management |
| Direct links | href URLs work when visited | Simple requests.get() |

