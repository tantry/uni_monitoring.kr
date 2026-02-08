# 🚀 Quick Reference Card

## **Most Frequently Used Documents**

### **Adding a New RSS Feed (5-minute start)**
```bash
# 1. Quick checklist
cat docs/UPSCALE_FEED_ADDITION_CHECKLIST.md

# 2. File templates
cat docs/UPSCALE_NEW_FEED_FILES_SUMMARY.txt

# 3. Full guide (when stuck)
less docs/UPSCALE_RSS_FEED_INTEGRATION_GUIDE.txt
```

### **Developing a New Scraper**
```bash
# CRITICAL: Read this first!
cat docs/UPSCALE_SCRAPER_DEVELOPMENT_GUIDE.md
```

### **Understanding the Architecture**
```bash
# Technical deep dive
cat docs/UPSCALE_RSS_PROJECT_STRUCTURE_ANALYSIS.txt | head -100
```

### **Planning Future Features**
```bash
# Complete roadmap
cat docs/UPSCALE_FUTURE_PROJECTS_ROADMAP.md

# Specific system: Deadlines
cat docs/UPSCALE_DEADLINE_INTEGRATION_PLAN.md
```

## **Common Tasks & Which Doc to Use**

| Task | Primary Document | Secondary Reference |
|------|------------------|---------------------|
| Add RSS feed | `FEED_ADDITION_CHECKLIST.md` | `RSS_FEED_INTEGRATION_GUIDE.txt` |
| Fix scraper issues | `SCRAPER_DEVELOPMENT_GUIDE.md` | `RSS_PROJECT_STRUCTURE_ANALYSIS.txt` |
| Plan new feature | `FUTURE_PROJECTS_ROADMAP.md` | (relevant integration plan) |
| Understand codebase | `RSS_PROJECT_STRUCTURE_ANALYSIS.txt` | `SCRAPER_DEVELOPMENT_GUIDE.md` |
| Implement deadlines | `DEADLINE_INTEGRATION_PLAN.md` | `FUTURE_PROJECTS_ROADMAP.md` |

## **One-Liners for Common Operations**

```bash
# Check if RSS feed is accessible
python3 -c "import feedparser; f=feedparser.parse('URL'); print('OK' if f.entries else 'FAIL')"

# Test scraper from project root
cd /path/to/uni_monitoring.kr && PYTHONPATH=. python3 scrapers/new_scraper.py

# Run monitor engine test
python3 core/monitor_engine.py --scrape-test

# Check documentation
grep -r "403 Forbidden" docs/  # Search for specific issue
```

## **Emergency Fixes (When Things Break)**

1. **ImportError: No module named 'core'**
   ```bash
   cd /path/to/uni_monitoring.kr
   PYTHONPATH=. python3 your_script.py
   ```

2. **RSS feed returns 403 Forbidden**
   - See: `UPSCALE_SCRAPER_DEVELOPMENT_GUIDE.md` - HTTP Headers section
   - Update User-Agent in scraper __init__

3. **No articles found**
   - See: `UPSCALE_SCRAPER_DEVELOPMENT_GUIDE.md` - Common Failure Patterns
   - Check feed.bozo flag in feedparser response

## **GitHub Ready Checklist**
- [ ] All docs in `docs/` folder
- [ ] No personal information in files
- [ ] `UPSCALE_` prefix on major documents
- [ ] `GUIDE_TO_DOCS.md` is current
- [ ] File names consistent with content
