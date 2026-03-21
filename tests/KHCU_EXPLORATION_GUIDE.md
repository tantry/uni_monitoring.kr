# KHCU Website Exploration Guide

## Current Status

✅ **Finding**: The KHCU website requires JavaScript rendering (like Adiga)
- Simple curl requests return 0 bytes
- Chrome browser is available on your system
- You have Selenium installed in your project

## Step 1: Run the Browser Explorer Script

This script uses Selenium to load the page in a real browser and analyze its structure:

```bash
cd ~/uni_monitoring.kr
python3 /tmp/khcu_browser_explorer.py
```

### What This Script Does:
1. Opens the KHCU site in a headless Chrome browser
2. Waits for JavaScript to render the content
3. Analyzes the HTML structure for:
   - Table elements
   - Class names and patterns
   - Links and clickable elements
   - Text content and dates
4. Saves the full rendered HTML to `/tmp/khcu_rendered.html`

### Expected Output:
```
🔍 KHCU Site Browser Exploration
============================================================

1️⃣  Starting Chrome browser...
   Loading: https://khcu.ac.kr/schedule/index.do
   Page title: [Title Here]
   Current URL: [URL Here]

2️⃣  Analyzing page structure...
   Total text content: XXXX characters
   Found X <table> elements
   First table has X rows

3️⃣  Looking for announcement/schedule containers...
   Found X elements with class containing 'notice'
   Found X elements with class containing 'schedule'
   ...

4️⃣  Looking for clickable elements (links)...
   Total links found: XX
   Sample links:
      1. [Link text here]
         href: [Link URL]
   ...

5️⃣  Looking for date/schedule information...
   [First 30 lines of page content]

6️⃣  HTML Structure Analysis...
   <div> elements: XXX
   <span> elements: XXX
   <p> elements: XX

7️⃣  Full rendered HTML saved to /tmp/khcu_rendered.html

✅ Exploration complete!
```

## Step 2: Inspect the Rendered HTML

After running the script, examine the saved HTML file:

```bash
# View it in less for easy navigation
less /tmp/khcu_rendered.html

# Or open in your text editor
code /tmp/khcu_rendered.html
nano /tmp/khcu_rendered.html
```

### Look For These Patterns:

1. **Announcement Container Structure**
   - Is there a main `<table>`?
   - Or `<div>` containers?
   - Any `<ul>` or `<ol>` lists?

   Example:
   ```html
   <table class="schedule-list">
     <tr>
       <td>Title</td>
       <td>Date</td>
       <td><a href="/detail/123">View</a></td>
     </tr>
   </table>
   ```

2. **Link Pattern for Articles**
   - Look for `<a href="/..." onclick="...">`
   - Check if links have IDs or parameters
   - Example patterns:
     - `/board/view/123`
     - `?id=123&dept=admission`
     - `onclick="openDetail('123')"`

3. **Title/Content Extraction**
   - Where are titles? (usually `<td>`, `<h3>`, or specific div)
   - Where is the date? (class names like `date`, `created_at`, etc.)
   - Any department/category indicators?

4. **Key CSS Classes/IDs**
   - Search for these patterns:
     ```
     class="schedule"
     class="notice"
     id="content"
     class="list-item"
     class="announcement"
     class="board"
     ```

## Step 3: Share Findings

Once you've examined the HTML, provide these details:

```
📊 KHCU Site Structure Report:

1. Main Container Type:
   ☐ Table-based layout
   ☐ Div-based cards
   ☐ List-based (ul/ol)
   ☐ Other: ___________

2. How many announcements visible per page? ___

3. Link Pattern (example URL from page):
   https://khcu.ac.kr/...

4. Title Location (HTML path):
   Example: <table class="schedule"><tr><td>TITLE HERE</td></tr>

5. Date Location (HTML path):
   Example: <span class="date">DATE HERE</span>

6. Any JavaScript patterns?
   ☐ onclick handlers for links
   ☐ fetch/AJAX calls
   ☐ React/Vue components
   ☐ Simple pagination

7. Does it require scrolling to load more?
   ☐ Yes, needs scrolling/pagination
   ☐ No, all visible on page load

8. Key CSS selectors to use:
   - For announcements: _____________
   - For titles: _____________
   - For links: _____________
   - For dates: _____________
```

## Step 4: Build the Scraper

Once we understand the structure, the scraper will follow this pattern:

```python
class KhcuScraper(BaseScraper):
    """Scraper for Kyung Hee Cyber University"""
    
    def __init__(self, config: dict):
        super().__init__(config)
        self.base_url = "https://khcu.ac.kr"
        self.source_name = "khcu"
        
    def fetch_articles(self) -> List[Dict]:
        """
        1. Use Selenium to load the page
        2. Wait for JavaScript to render
        3. Find announcement containers using CSS selectors
        4. Extract title, link, date from each
        5. Return list of article dicts
        """
        articles = []
        
        # TODO: Implement based on discovered selectors
        
        return articles
    
    def parse_article(self, raw_data: Dict) -> Article:
        """
        1. Clean up title and content
        2. Detect department using filter_engine
        3. Create Article object
        4. Return parsed article
        """
        # TODO: Implement based on discovered data structure
        pass
```

## Troubleshooting

### Script fails to load page:
```bash
# Check if Chrome is working
google-chrome --version

# Try increasing wait time in the script
# Modify: time.sleep(3) to time.sleep(5)
```

### No elements found:
- The page may have loaded but is still rendering
- Increase the sleep time
- Check if the URL is correct
- Look for iframe elements (content might be in iframe)

### HTML is empty:
- Server might be blocking automated access
- Try adding different user agents
- Check if there's a cookie consent requirement

## Next Steps

1. ✅ Run the explorer script
2. ✅ Examine `/tmp/khcu_rendered.html`
3. ✅ Share findings using the report format above
4. 🚀 Create the scraper implementation based on your findings

---

**Questions?** Share the output or the `/tmp/khcu_rendered.html` file contents, and I'll help you build the scraper!
