# UPSCALE Source Integration Requirements

## Overview
This document specifies what Article fields are expected, optional, and how different source types provide them.

---

## Article Model - Core vs Optional Fields

### Core Fields (Required)
All articles must have these:

```python
@dataclass
class Article:
    title: str              # Article headline
    url: str                # URL to full article
    content: str            # Article body text
    source: str             # Source identifier (adiga, unn_news, etc)
    published_date: Optional[str] = None  # ISO format or parsed string
    department: Optional[str] = None      # Detected department (music, korean, etc)
```

### Extended Fields (Optional by Source Type)
Different sources provide different metadata:

```python
# RSS Sources provide:
author: Optional[str]           # Author name (UNNNewsScraper)
categories: Optional[List[str]] # Tags/categories (UNNNewsScraper)
summary: Optional[str]          # Summary or excerpt (UNNNewsScraper)
rss_id: Optional[str]           # Unique ID from RSS feed

# Web Scrapers may provide:
university: Optional[str]       # University name
admission_type: Optional[str]   # 수시, 정시, 추가합격
deadline: Optional[str]         # Application deadline
scraped_at: Optional[str]       # When scraped

# API Sources may provide:
image_url: Optional[str]        # Article image
update_timestamp: Optional[str]  # Last update time
raw_metadata: Optional[dict]    # Source-specific data
```

---

## Source Type Specifications

### Type 1: Web Scraper (Selenium/BeautifulSoup)
**Example:** AdigaScraper

#### Fields Provided
```python
{
    'title': 'Article title from page',
    'url': 'https://adiga.kr/...',
    'content': 'Extracted article body',
    'source': 'adiga',
    'published_date': '2026-02-09',
    'department': None  # Detected later by FilterEngine
}
```

#### Characteristics
- Extracts from HTML structure
- May have JavaScript-rendered content (requires Selenium)
- Content length variable
- URLs directly clickable

#### Integration Steps
1. Inherit from `BaseScraper`
2. Implement `fetch_articles()` → returns List[Dict]
3. Implement `parse_article()` → returns Article
4. Add to `config/sources.yaml` with `scraper_class`
5. Handle missing fields gracefully in parse_article

---

### Type 2: RSS Feed
**Example:** UNNNewsScraper

#### Fields Provided
```python
{
    'title': 'Article title from RSS item',
    'url': 'https://news.unn.net/news/articleView.html?...',
    'content': 'Article content or summary',
    'source': 'unn_news',
    'published_date': '2026-02-06T17:19:29',
    'author': 'Reporter Name',
    'categories': ['Category1', 'Category2'],
    'summary': 'Brief summary if provided',
    'rss_id': 'unn_1',
    'department': None  # Detected later
}
```

#### Characteristics
- Standardized XML format
- Limited content depth (usually summary only)
- Author and categories common
- Consistent field names across items

#### Integration Steps
1. Inherit from `BaseScraper`
2. Use feedparser library to parse RSS
3. Extract title, link (as url), description/content
4. Parse published_date to ISO format
5. Extract optional: author, categories
6. Add to `config/sources.yaml`

#### Important: Handle Extra Fields
```python
def parse_article(self, raw_data: Dict) -> Article:
    # Create Article with only known fields
    article = Article(
        title=raw_data.get('title', ''),
        url=raw_data.get('url', ''),
        content=raw_data.get('content', ''),
        source=self.source_name,
        published_date=raw_data.get('published_date'),
        department=None
    )
    
    # Store extra fields in metadata or ignore
    # Don't try to pass author, categories to Article.__init__
    return article
```

---

### Type 3: JSON API
**Future:** University API endpoints

#### Fields Provided
```python
{
    'title': 'API response title',
    'url': 'https://api.university.edu/notice/123',
    'content': 'Full content from API',
    'source': 'university_api',
    'published_date': '2026-02-09T10:00:00Z',
    'university': 'Seoul University',
    'admission_type': '정시',
    'deadline': '2026-03-15',
    'department': None
}
```

#### Characteristics
- Structured JSON response
- Consistent field names
- Rich metadata available
- Faster than web scraping

---

## Field Handling Best Practices

### For Each Scraper's `parse_article()` Method

```python
def parse_article(self, raw_data: Dict) -> Article:
    """
    Parse raw data into Article model.
    
    Handle extra fields gracefully:
    - Only pass known Article fields to __init__
    - Store source-specific fields elsewhere if needed
    - Don't fail if optional fields missing
    """
    try:
        article = Article(
            # Required fields - always provide
            title=raw_data.get('title', 'Untitled'),
            url=raw_data.get('url', ''),
            content=raw_data.get('content', ''),
            source=self.source_name,
            
            # Optional fields - may be None
            published_date=self._parse_date(raw_data.get('published_date')),
            department=None  # Always None here - set by FilterEngine later
        )
        
        # If you need to preserve extra fields:
        # Option 1: Store in a separate metadata dict
        # Option 2: Create subclass of Article
        # Option 3: Log them but don't store
        
        return article
        
    except Exception as e:
        self.logger.error(f"Error parsing article: {e}")
        return None
```

### Date Parsing Helper
```python
def _parse_date(self, date_str: str) -> Optional[str]:
    """Convert various date formats to ISO format"""
    if not date_str:
        return None
    
    try:
        from dateutil import parser
        dt = parser.parse(date_str)
        return dt.isoformat()
    except:
        return None
```

---

## Configuration Requirements

### In `config/sources.yaml`

**Minimum required:**
```yaml
sources:
  source_id:
    name: "Display Name"
    url: "https://..."
    enabled: true
    scraper_class: "module_name"  # Must match scrapers/module_name.py
```

**Recommended:**
```yaml
sources:
  source_id:
    name: "Display Name"
    url: "https://..."
    enabled: true
    scraper_class: "module_name"
    scrape_interval: 1800           # Seconds between scrapes
    description: "What this source provides"
    
    # Source-specific config (passed to scraper)
    timeout: 30                     # For web scrapers
    headers:                        # Custom headers
      User-Agent: "Custom/1.0"
    
    # Type-specific settings
    type: "rss"                    # or "web", "api"
    quality_rules:
      min_content_length: 50
      reject_patterns: [...]
      accept_keywords: [...]
```

---

## FilterEngine Configuration

### In `config/filters.yaml`

```yaml
matching:
  strategy: "contains"            # exact, contains, regex, fuzzy
  min_confidence: 0.15            # 15% - very permissive
  enable_fallback: true

departments:
  music:
    name: "음악학과"
    keywords: ["음악", "music", "실용음악", "성악", "작곡"]
    emoji: "🎵"
    priority: 1
```

**Confidence Threshold Notes:**
- `0.05-0.10`: Very permissive (noisy but catches everything)
- `0.15`: Default (balanced)
- `0.25-0.33`: Medium (1-2 keywords out of 7)
- `0.50`: Strict (half keywords must match)
- `0.70`: Very strict (most keywords must match)

**For different sources:**
- Web scrapers (adiga): Can use higher threshold (more keywords in content)
- RSS feeds (unn_news): Should use lower threshold (less content)

---

## Testing New Source

### Step 1: Test Scraper in Isolation
```bash
python3 scrapers/your_scraper.py
```

Should output:
```
✅ Scraper initialized
✅ Fetched articles
Found X articles
```

### Step 2: Test Article Parsing
```python
from scrapers.your_scraper import YourScraper

scraper = YourScraper({'url': 'https://...'})
articles = scraper.fetch_articles()

# Check each article
for article in articles:
    assert article.title, "Missing title"
    assert article.url, "Missing URL"
    assert article.content, "Missing content"
    assert article.source, "Missing source"
    print(f"✅ {article.title}")
```

### Step 3: Test with FilterEngine
```python
from core.filter_engine import FilterEngine

fe = FilterEngine()
for article in articles:
    dept = fe.detect_department(article)
    print(f"Detected: {dept}")
```

### Step 4: Integration Test
```bash
python3 core/monitor_engine.py --test
```

Should show:
- Scraper loading
- Articles found
- Departments detected
- Telegram format (test mode)

---

## Troubleshooting

| Error | Cause | Solution |
|-------|-------|----------|
| `ModuleNotFoundError: 'scrapers.xyz'` | scraper_class config wrong | Check spelling in sources.yaml |
| `No class found matching xyz_scraper` | Python class name doesn't match convention | Rename class to match (YzScraper for yz_scraper) |
| `got an unexpected keyword argument 'field'` | Passing extra fields to Article.__init__ | Only pass known Article fields |
| `0 articles found` | Low confidence threshold or no keyword matches | Adjust matching.min_confidence in filters.yaml |
| `50 articles parsed, 0 articles returned` | parse_article() errors silently | Check logs - fix exception handling |

---

## Summary: Adding a New Source

1. **Create scraper** at `scrapers/new_source.py`
   - Inherit from BaseScraper
   - Implement fetch_articles(), parse_article(), get_source_name()
   - Handle all field types gracefully

2. **Add to config** in `config/sources.yaml`
   - source_id
   - name, url, enabled
   - **scraper_class: "new_source"**

3. **Test isolation** with `python3 scrapers/new_source.py`

4. **Test integration** with `python3 core/monitor_engine.py --test`

5. **Verify** articles appear with departments detected

6. **Adjust** `filters.yaml` min_confidence if needed

---

**Last Updated:** 2026-02-09  
**Tested Sources:** adiga_scraper (web), unn_news_scraper (RSS)  
**Status:** Ready for new source integration
