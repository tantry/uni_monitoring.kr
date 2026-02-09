# UPSCALE Architecture Decisions

## Overview
This document captures key architectural decisions, issues discovered, and their solutions during integration of the robust scraper system.

---

## 1. YAML Configuration Requirements

### Decision
All scrapers must be declared in `config/sources.yaml` with explicit `scraper_class` mapping.

### Issue Found
- `sources.yaml` was missing `scraper_class` field for both adiga and unn_news
- Factory couldn't determine which Python class to instantiate
- Result: Only adiga ran, unn_news was ignored silently

### Solution
```yaml
sources:
  adiga:
    scraper_class: "adiga_scraper"  # Maps to AdigaScraper class
    # ... other config ...
  
  unn_news:
    scraper_class: "unn_news_scraper"  # Maps to UNNNewsScraper class
    # ... other config ...
```

### Rationale
- Factory uses `scraper_class` to dynamically import and instantiate scrapers
- Naming convention: snake_case in config maps to PascalCase class names
- Enables pluggable architecture without hardcoding

---

## 2. FilterEngine Confidence Threshold

### Decision
Minimum confidence threshold for department matching should be configurable in `config/filters.yaml`, not hardcoded.

### Issue Found
- `FilterEngine.__init__` hardcoded `self.min_confidence = 0.7` (70%)
- With only 2 keyword matches out of 7, confidence = 2/7 = 0.286 (28.6%)
- No articles matched any department filter
- Result: Articles found but all filtered out

### Solution
```yaml
# config/filters.yaml
matching:
  min_confidence: 0.15  # 15% - any keyword match counts
```

```python
# core/filter_engine.py
matching_config = self.config_data.get('matching', {})
self.min_confidence = float(matching_config.get('min_confidence', 0.15))
```

### Rationale
- Different sources have different keyword density
- 15% threshold = if 1 keyword matches out of 7, article gets categorized
- Configurable allows tuning without code changes
- Default to 0.15 for new deployments

---

## 3. MonitorEngine Must Use ScraperFactory

### Decision
`monitor_engine.py` must use `ScraperFactory.create_all_enabled()` instead of hardcoding scraper instantiation.

### Issue Found
```python
# OLD - Hardcoded only AdigaScraper
scrapers = []
if 'adiga' in sources_config.get('sources', {}):
    scrapers.append(AdigaScraper(adiga_config))
```
- Only AdigaScraper ran
- UNNNewsScraper never instantiated
- UNNNewsScraper not in imports anymore = harder to maintain

### Solution
```python
# NEW - Uses factory
from core.scraper_factory import ScraperFactory
factory = ScraperFactory()
scrapers = factory.create_all_enabled()
```

### Rationale
- Factory discovers all enabled sources from config
- Scales to any number of new scrapers
- No code changes needed to add sources
- Maintains single source of truth (sources.yaml)

---

## 4. Article Model Must Accept Optional Fields

### Decision
Article dataclass must support optional fields from any source type (web scraper vs RSS feed vs API).

### Issue Found
- UNNNewsScraper passes: `author`, `categories`, `summary`, `rss_id`
- Article model only had: `title`, `url`, `content`, `source`, `published_date`, `department`
- Error: `Article.__init__() got an unexpected keyword argument 'author'`
- Result: 50 articles parsed from RSS, 0 successfully created

### Solution
Extend Article model to accept and ignore extra fields via **kwargs or explicit optional fields.

See `UPSCALE_SOURCE_INTEGRATION_REQUIREMENTS.md` for detailed field handling.

### Rationale
- Different sources provide different metadata
- RSS feeds include: author, categories, summary
- Web scrapers may include: university, admission_type, deadline
- API sources may include: update_timestamp, image_url
- Model should be permissive, not strict

---

## 5. FilterEngine Accepts Both Article Objects and Dicts

### Decision
`FilterEngine.detect_department()` must accept both:
- Article objects (from new architecture)
- Dict objects (for backward compatibility and direct usage)

### Implementation
```python
def detect_department(self, article, title=None):
    # Handle both Article objects and dictionaries
    if isinstance(article, dict):
        article_text = article.get('content', '')
        if not title:
            title = article.get('title')
    else:
        # Assume it's an Article object
        article_text = article.content if hasattr(article, 'content') else str(article)
        if not title and hasattr(article, 'title'):
            title = article.title
```

### Rationale
- Robust interface for multiple use cases
- Legacy code can pass dicts
- New code uses Article objects
- Type-agnostic implementation

---

## 6. Configuration Loading Order in FilterEngine

### Decision
FilterEngine must load full config before accessing nested values.

### Issue Found
```python
# OLD - Accessed config_data before loading it
self.min_confidence = float(matching_config.get('min_confidence', 0.15))
# But self.config_data wasn't set yet!
```

### Solution
```python
def __init__(self, config_path: str = "config/filters.yaml"):
    self.config_path = Path(config_path)
    # Load config FIRST
    self.config_data = self._load_config()
    # THEN access it
    matching_config = self.config_data.get('matching', {})
    self.min_confidence = float(matching_config.get('min_confidence', 0.15))
```

### Rationale
- Initialization order matters
- Dependencies must be satisfied before use
- Clear separation of load → configure → ready states

---

## Summary of Key Decisions

| Component | Decision | Reason |
|-----------|----------|--------|
| sources.yaml | Explicit scraper_class mapping | Factory needs to know which class to load |
| filters.yaml | Configurable matching thresholds | Different sources have different keyword density |
| monitor_engine | Use ScraperFactory | Scales to any number of sources |
| Article model | Accept optional fields | Different sources provide different metadata |
| FilterEngine | Accept Article or dict | Backward compatible and flexible |

---

## Impact on New Source Addition

When adding a new scraper, these decisions ensure:
1. ✅ Config-driven registration (no code changes to factory)
2. ✅ Flexible field handling (each source brings own fields)
3. ✅ Smart filtering (configurable thresholds per source type)
4. ✅ Automatic discovery (factory finds all enabled sources)
5. ✅ Backward compatibility (legacy dict-based code still works)

---

**Last Updated:** 2026-02-09  
**Session:** Integration testing and multi-scraper verification  
**Status:** ✅ All decisions implemented and tested
