# RSS Feed Addition Checklist

## Quick Reference for Adding New RSS Feeds

### Phase 1: Pre-Integration Analysis
- [ ] Feed URL accessible (curl -I <URL>)
- [ ] Feed structure analyzed (python3 -c "import feedparser; ...")
- [ ] Required fields confirmed: title, link, content(summary/description)
- [ ] Dependencies installed: feedparser, python-dateutil

### Phase 2: Scraper Implementation
- [ ] File created: `scrapers/[source]_scraper.py`
- [ ] Imports: BaseScraper, Article, feedparser
- [ ] Class: `[Source]Scraper(BaseScraper)`
- [ ] `__init__`: Sets source_name, base_url, headers
- [ ] `fetch_articles()`: Returns List[Dict] with articles
- [ ] `parse_article()`: Returns Article object
- [ ] `get_source_name()`: Returns string identifier
- [ ] Content extraction method (`_extract_content()`)
- [ ] Date parsing method (`_parse_date()`)
- [ ] HTML cleaning method (`_clean_html()`)

### Phase 3: Configuration
- [ ] `config/sources.yaml`: Added source entry
- [ ] Fields: name, url, enabled, scrape_interval
- [ ] `core/scraper_factory.py`: Added import and registration
- [ ] Import line: `from scrapers.[source]_scraper import [Source]Scraper`
- [ ] Registration: `if source_name == "[source]": return [Source]Scraper(config)`

### Phase 4: Testing
- [ ] Direct test: `PYTHONPATH=. python3 scrapers/[source]_scraper.py`
- [ ] Factory test: Created via scraper_factory.create_scraper()
- [ ] Integration test: `python3 core/monitor_engine.py --scrape-test`
- [ ] Log check: No errors in monitor.log
- [ ] Article validation: All articles have title, url, content
- [ ] Department detection: Articles categorized correctly

### Phase 5: Deployment
- [ ] Test mode successful: `python3 core/monitor_engine.py --test`
- [ ] Production run: `python3 core/monitor_engine.py` (no --test flag)
- [ ] Notifications: Verify Telegram messages format
- [ ] Database: Articles stored in data/state.db

---

## Common Issues & Quick Fixes

### ImportError: No module named 'core'
```bash
# Run from project root
cd /path/to/uni_monitoring.kr
PYTHONPATH=. python3 script.py
```

### 403 Forbidden on RSS Feed
```python
# Update headers in scraper __init__
self.session.headers.update({
    'User-Agent': 'Mozilla/5.0 (compatible; uni_monitoring.kr/1.0)',
    'Accept': 'application/rss+xml, application/xml, */*',
})
```

### No Articles Found
```python
# Check feedparser response
feed = feedparser.parse(url)
print('Entries:', len(feed.entries))
print('Bozo error:', feed.bozo, feed.bozo_exception if feed.bozo else 'None')
```

### Dates Not Parsing
```python
# Use feedparser's parsed date first
if hasattr(entry, 'published_parsed') and entry.published_parsed:
    dt = datetime.fromtimestamp(time.mktime(entry.published_parsed))
    return dt.strftime('%Y-%m-%d %H:%M:%S')
```

---

## File Templates

### sources.yaml Entry
```yaml
source_key:
  name: "Display Name"
  url: "https://feed.url/rss.xml"
  enabled: true
  scrape_interval: 1800
  description: "Optional description"
```

### Scraper Factory Registration
```python
# Add to imports
from scrapers.source_scraper import SourceScraper

# Add to create_scraper function
if source_name == "source_key":
    return SourceScraper(config)
```

### Basic RSS Scraper Template
```python
from core.base_scraper import BaseScraper
from models.article import Article
import feedparser

class SourceScraper(BaseScraper):
    def __init__(self, config):
        super().__init__(config)
        self.source_name = "source_key"
        self.base_url = config.get('url', '')
    
    def fetch_articles(self):
        feed = feedparser.parse(self.base_url)
        articles = []
        for entry in feed.entries:
            articles.append({
                'title': entry.get('title', '').strip(),
                'url': entry.get('link', ''),
                'content': self._extract_content(entry),
                'published_date': self._parse_date(entry),
                'source': self.source_name,
            })
        return articles
    
    def parse_article(self, raw_data):
        return Article(**raw_data)
    
    def get_source_name(self):
        return self.source_name
```

---

## Verification Commands

```bash
# 1. Check feed accessibility
curl -s -o /dev/null -w "%{http_code}" https://feed.url/rss.xml

# 2. Check feed structure
python3 -c "
import feedparser
f=feedparser.parse('https://feed.url/rss.xml')
print('Status:', 'OK' if not f.bozo and f.entries else 'ERROR')
print('Entries:', len(f.entries))
if f.entries:
    print('First entry keys:', list(f.entries[0].keys()))
"

# 3. Test scraper directly
cd /path/to/uni_monitoring.kr
PYTHONPATH=. python3 scrapers/new_scraper.py

# 4. Test integration
python3 core/monitor_engine.py --scrape-test 2>&1 | grep -A5 -B5 "source_key"

# 5. Check logs
tail -20 logs/monitor.log | grep -i "source_key\|error\|exception"
```

---

## Success Criteria

- [ ] Feed returns HTTP 200
- [ ] Feed has entries (>0)
- [ ] Scraper parses all entries without errors
- [ ] All articles have title, url, content
- [ ] Dates parsed correctly
- [ ] Articles appear in monitor engine output
- [ ] No errors in logs
- [ ] Department detection works (some articles categorized)
- [ ] Notifications sent in test mode
