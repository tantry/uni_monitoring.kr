Message to assistant:

I'm a new developer onboarding to this university monitoring project. 
reference https://github.com/tantry/uni_monitoring.kr 
I need to add a new RSS feed from https://news.unn.net/rss/allArticle.xml. I have access, but you do not, to the project documentation at docs/. Walk me through the complete integration process using the established patterns and fix any issues we encounter. confirm you are done making initial exploration then i will issue a command to show you my exact file situation 

(User: Start by running this block, copy results, paste into prompt)

sqlite3 data/state.db "SELECT COUNT(*) as total, department, COUNT(DISTINCT source) as sources FROM articles GROUP BY department;"
```
echo "=== TEST: New developer adding RSS feed ==="
echo "1. They check GUIDE_TO_DOCS.md"
cat docs/GUIDE_TO_DOCS.md | grep -A5 "Getting Started"
echo ""
echo "2. They follow the checklist"
cat docs/UPSCALE_FEED_ADDITION_CHECKLIST.md | grep -E "^### Phase|^- \[ \]"
echo ""
echo "3. They check for common issues"
grep -n "403 Forbidden\|ModuleNotFoundError" docs/UPSCALE_SCRAPER_DEVELOPMENT_GUIDE.md
```
Key Issues to Resolve
   1. Import path resolution (ModuleNotFoundError: 'core')
   2. Factory registration in scraper_factory.py
   3. Testing integration with monitor engine
   4. Department filtering verification
- assist user step-by-step
- base your suggestions only on the facts I provide about my system current state
- stop and allow me to choose an option.
- user prefers execution of exploratory or implementation to working system safely, so do explain the changes to system
- user absolutely prefers sed, cat, cat EOF commands, or nano commands where absolutely required. 

# 1. Show current directory
```
pwd
```
# 2. List your project files
```
ls -la
```
# 3. Show current monitor_engine.py filter logic
```
cat core/monitor_engine.py | grep -A 20 "def filter_article"
```
# 4. Show filters.yaml content
```
cat config/filters.yaml
```
# 5. Show recent monitor run output (if available)
```
tail -50 logs/monitor.log  # or whatever your last run showed
```
# 6. Check if database has articles
```
sqlite3 data/state.db "SELECT COUNT(*) as total, department, COUNT(DISTINCT source) as sources FROM articles GROUP BY department;"
```
   **NOTE for AI PROMPTS**
(add this at end of every third subsequent prompt)
- assist user step-by-step
- base your suggestions only on the facts I provide about my system current state
- stop and allow me to choose an option.
- user prefers execution of exploratory or implementation to working system safely, so do explain the changes to system
- user absolutely prefers sed, cat, cat EOF commands, or nano commands where absolutely required. 


---

Test new RSS - Python
to add:
https://www.iscu.ac.kr/rss.xml
test to see first with feedparser

```
python3 << 'PYTHON'
import feedparser

url = "https://www.iscu.ac.kr/rss.xml"
feed = feedparser.parse(url)

print(f"Feed title: {feed.feed.get('title', 'N/A')}")
print(f"Feed entries: {len(feed.entries)}")
print(f"Bozo: {feed.bozo}")

if feed.bozo:
    print(f"Bozo exception: {feed.bozo_exception}")

if feed.entries:
    print(f"\nFirst entry:")
    print(f"  Title: {feed.entries[0].get('title', 'N/A')}")
    print(f"  Link: {feed.entries[0].get('link', 'N/A')}")
else:
    print("No entries found in feed")
PYTHON
```
now edit

```
nano config/sources.yaml
```
advised: remember that yaml disallows TABS never use tabs, only use spaces (try copy this or edit one inside the config/sources.yaml)

```
seoul_cyber_uni:
    name: "Seoul Cyber University"
    url: "https://www.iscu.ac.kr/rss.xml"
    enabled: true
    scraper_class: "rss_feed_scraper"
    scrape_interval: 1800
```

```
python3 core/monitor_engine.py --test 2>&1 | grep -A 15 "seoul_cyber_uni"
```



testing scraper_class


push to telegram, first

```
rm -f state.json  
```




