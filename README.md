# 🎓 University Admission Monitor

Automated Korean university admission announcement monitoring system with real-time Telegram notifications.

## ✨ Features

* **Multi-Source Monitoring**: Scrapes admission announcements from Korean education portals
* **Multi-Department Tracking**: Music, Korean, English, Liberal Arts departments
* **Real-time Alerts**: Telegram notifications for new announcements
* **Intelligent Filtering**: Keyword-based content filtering
* **Duplicate Detection**: SQLite-based deduplication
* **Selenium Support**: Handles JavaScript-rendered content and popups
* **Safe GitHub Integration**: Interactive review before pushing

## 🚀 Quick Start

### Prerequisites
```bash
# System packages (Manjaro/Arch)
sudo pacman -S python python-pip google-chrome-beta chromedriver

# Python packages
pip install requests beautifulsoup4 pyyaml selenium
```

### Installation
```bash
git clone https://github.com/tantry/uni_monitoring.kr.git
cd uni_monitoring.kr
```

### Configuration

1. **Telegram Setup**:
   - Create bot via @BotFather → get `BOT_TOKEN`
   - Create channel → get `CHAT_ID`
   - Add bot as admin to channel

2. **Edit config/config.yaml**:
```yaml
telegram:
  bot_token: "YOUR_BOT_TOKEN"
  chat_id: "YOUR_CHAT_ID"
```

### Run Monitor
```bash
# Test mode (no Telegram)
python3 core/monitor_engine.py --test

# Production mode
./check_now.sh
```

## 📋 Project Structure
```
uni_monitoring.kr/
├── config/                     # YAML configurations
├── core/                       # Core engine (monitor, filters, factory)
├── models/                     # Data models (Article)
├── scrapers/                   # Site-specific scrapers
│   ├── adiga_scraper.py       # ✅ Working (Selenium + popups)
│   └── scraper_template.py    # Template for new scrapers
├── notifiers/                  # Telegram notifications
├── data/                       # SQLite database
├── logs/                       # Application logs
├── SCRAPER_DEVELOPMENT_GUIDE.md  # ⭐ Critical reference
└── check_now.sh               # Main monitoring script
```

## 🔧 Adiga Scraper - Technical Details

### The Challenge
Adiga.kr uses JavaScript popups (`fnDetailPopup()`) instead of direct article URLs. Articles cannot be accessed via GET requests.

### The Solution
**Selenium-based popup clicking**:
1. Initialize headless Chrome with proper ChromeDriver
2. Navigate to news page
3. Find links with `onclick="fnDetailPopup('ID')"`
4. Click each link to open popup
5. Extract content from popup
6. Close popup, repeat

### Key Code Pattern
```python
# Find popup links
popup_links = driver.find_elements(By.XPATH, "//a[contains(@onclick, 'fnDetailPopup')]")

for link in popup_links:
    # Click to open popup
    driver.execute_script("arguments[0].click();", link)
    time.sleep(2)
    
    # Extract popup content
    page_source = driver.page_source
    soup = BeautifulSoup(page_source, 'html.parser')
    popup = soup.find('div', class_='popCont')
    content = popup.get_text(strip=True) if popup else ""
```

## 📚 Adding New Scrapers

**IMPORTANT**: Read `SCRAPER_DEVELOPMENT_GUIDE.md` first!

### Pre-Development Checklist
- [ ] Check if site requires cookies (Korean sites usually do)
- [ ] Check if content is JavaScript-rendered (view page source)
- [ ] Test if article links work directly or open popups
- [ ] Identify the pattern: Simple HTTP / Selenium / Popup clicking

### Steps
1. Copy `scrapers/scraper_template.py`
2. Follow the template's pattern selection
3. Test standalone: `python3 scrapers/your_scraper.py`
4. Add to `config/sources.yaml`
5. Test with monitor: `python3 core/monitor_engine.py --test`

## 🐛 Troubleshooting

### Selenium Issues
**ChromeDriver version mismatch**:
```bash
# Check versions
/usr/bin/google-chrome-beta --version
/usr/bin/chromedriver --version

# Should match major version (e.g., both 145.x)
```

**Solution**: Install matching ChromeDriver beta
```bash
sudo pacman -S chromedriver-beta
```

### No Articles Found
1. Check if cookies need acceptance (see SCRAPER_DEVELOPMENT_GUIDE.md)
2. View page source - is HTML minimal? → Use Selenium
3. Test article URLs manually - do they work?
4. Check `selenium_page_source.html` debug file

### Empty Article Content
- Likely popup-based articles (Adiga pattern)
- URLs don't lead to content pages
- Must click links with Selenium to trigger popups

### Telegram Not Working
```bash
# Test bot token
curl "https://api.telegram.org/bot<YOUR_TOKEN>/getMe"

# Check logs
tail -f logs/monitor.log
```

## 🎯 Current Status

### ✅ Working
- Adiga scraper (Selenium + popup extraction)
- Telegram notifications
- Duplicate detection
- Department filtering
- Safe GitHub integration

### 📋 Next Steps
- Add more university sources
- Implement cron automation
- Web dashboard for monitoring

## 📖 Documentation

- **SCRAPER_DEVELOPMENT_GUIDE.md** - Critical patterns and solutions
- **scrapers/scraper_template.py** - Comprehensive template with examples
- **config/** - YAML configuration examples

## 🤝 Contributing

1. Read SCRAPER_DEVELOPMENT_GUIDE.md
2. Use scraper_template.py
3. Test thoroughly before submitting
4. Document any new patterns discovered

## 📄 License

MIT License

---

**Last Updated**: 08 February 2026  
**Maintainer**: tantry  
**Status**: ✅ Production Ready
