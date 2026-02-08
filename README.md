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
pip install -r requirements.txt
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
database:
  path: "data/state.db"
logging:
  level: "INFO"
  file: "logs/monitor.log"
```

3. **Copy example configs**:
```bash
cp config/config.example.yaml config/config.yaml
cp config/sources.example.yaml config/sources.yaml
cp config/filters.example.yaml config/filters.yaml
```

### Run Monitor
```bash
# Test mode (no Telegram)
python3 core/monitor_engine.py --test

# Production mode
./check_now.sh

# Legacy mode
python3 multi_monitor.py
```

## 📋 Project Structure
```
uni_monitoring.kr/
├── config/                     # Configuration management
│   ├── config.yaml            # Main configuration
│   ├── sources.yaml           # Scraper source definitions
│   └── filters.yaml           # Department filtering rules
├── core/                      # Core business logic
│   ├── base_scraper.py        # Abstract base class for all scrapers
│   ├── monitor_engine.py      # Main monitoring orchestrator
│   ├── scraper_factory.py     # Factory for creating scraper instances
│   ├── filter_engine.py       # Advanced filtering engine
│   └── state_manager.py       # Database-backed state management
├── models/                    # Data models
│   └── article.py             # Article data class (Pydantic model)
├── scrapers/                  # Site-specific scrapers
│   ├── adiga_scraper.py       # ✅ Working (Selenium + popups)
│   ├── scraper_template.py    # Template for new scrapers (⭐ Use this!)
│   └── scraper_base.py        # Legacy base scraper (deprecated)
├── notifiers/                 # Telegram notifications
│   └── telegram_notifier.py   # Telegram notification handler
├── filters/                   # Filter implementations
│   └── department_filter.py   # Department-based filtering
├── tests/                     # Test suite
├── utils/                     # Utility functions
├── scripts/                   # Utility scripts
├── data/                      # Data storage
│   ├── state.db               # SQLite database (auto-generated)
│   └── adiga/                 # Adiga-specific data
├── logs/                      # Log files
│   └── monitor.log            # Application logs (auto-generated)
├── multi_monitor.py           # Legacy monitoring orchestrator
├── push_to_github_safe.sh     # Safe GitHub push with review steps
├── setup_github_safe.sh       # Complete GitHub setup script
├── push_to_github.sh          # Original GitHub push script
├── check_now.sh               # Main monitoring script
├── SCRAPER_DEVELOPMENT_GUIDE.md  # ⭐ Critical reference for scraper development
└── README.md                  # This file
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

### Scraper Template Structure
```python
"""
Template for new scraper implementations
"""
import logging
from typing import List, Dict, Optional
from core.base_scraper import BaseScraper
from models.article import Article

logger = logging.getLogger(__name__)

class NewSourceScraper(BaseScraper):
    """Scraper for [Source Name]"""
    
    def __init__(self, config: dict):
        super().__init__(config)
        self.base_url = "https://example.com"
        self.source_name = "new_source"
    
    def fetch_articles(self) -> List[Dict]:
        # Implementation here
        pass
    
    def parse_article(self, raw_data: Dict) -> Article:
        # Parse raw article data into Article model
        pass
    
    def detect_department(self, article_data: Dict) -> Optional[str]:
        """
        Detect which department this article belongs to.
        
        Returns:
            Department name or None
        """
        content = f"{article_data.get('title', '')} {article_data.get('content', '')}"
        content_lower = content.lower()
        
        # Department keyword mapping
        department_keywords = {
            'music': ['음악', '실용음악', '성악', '작곡', 'music'],
            'korean': ['한국어', '국어국문', '국문학', '국어'],
            'english': ['영어', '영어영문', '영문학', 'english'],
            'liberal': ['인문', '인문학', '교양교육', '교양'],
        }
        
        for dept, keywords in department_keywords.items():
            if any(keyword in content_lower for keyword in keywords):
                return dept
        
        return None
```

### Adding New Source Configuration
1. Add source to `config/sources.yaml`:
```yaml
new_source:
  name: "New Source Name"
  url: "https://example.com"
  enabled: true
  scrape_interval: 3600  # seconds
  description: "Description of the source"
```

2. Register scraper in `core/scraper_factory.py`:
```python
from scrapers.new_source_scraper import NewSourceScraper

def create_scraper(source_name: str, config: dict) -> Optional[BaseScraper]:
    if source_name == "new_source":
        return NewSourceScraper(config)
    # ... existing scrapers
```

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

## 🤖 Telegram Integration

The system sends formatted Telegram messages:

```
🎵 [새 입학 공고] 서울대학교 음악학과 추가모집

📌 부서/학과: music
📝 내용: 서울대학교 음악학과에서 2026학년도 추가모집을 실시합니다...
🔗 링크: https://adiga.kr/ArticleDetail.do?articleID=26546

#대학입시 #music
```

## 📊 Current Data Sources

### Adiga (어디가)
* **URL**: https://www.adiga.kr
* **Status**: ✅ Active (Selenium + Popup Solution Working)
* **Coverage**: General admission news and announcements
* **Pattern**: JavaScript popups requiring Selenium click simulation

### Target Universities for Future Development
1. **서울대학교** - https://admission.snu.ac.kr
2. **연세대학교** - https://admission.yonsei.ac.kr  
3. **고려대학교** - https://admission.korea.ac.kr
4. **한국대학교** - Individual department pages

## 🎯 Architecture Status

### ✅ Completed Foundation
* **New Core Architecture**: `core/base_scraper.py`, `core/filter_engine.py`, `core/scraper_factory.py`
* **Enhanced Configuration**: YAML-based configs in `config/` directory
* **Data Models**: `models/article.py` for standardized article representation
* **State Management**: SQLite database for reliable state tracking
* **Safe GitHub Integration**: Interactive push scripts with review steps
* **Adiga Scraper**: Working Selenium implementation with popup handling

### 🔄 In Progress
* **Content Discovery**: Finding actual admission announcement URLs on Adiga.kr
* **Template System**: Creating reusable scraper templates
* **Deadline System Integration**: Integrating deadline tracking into main architecture

### 📋 Pending
* **Additional Sources**: Implementing scrapers for target universities
* **RSS Sources**: Adding RSS feed monitoring capabilities
* **Testing Framework**: Comprehensive test suite
* **Web Dashboard**: Monitoring status interface

## 🔄 Upcoming: Deadline System Integration

The deadline tracking system will be integrated into the main architecture:

**Plan**:
- **Phase 1**: Fix admission scraper (✅ Completed)
- **Phase 2**: Create `deadline_source.py` and integrate with monitor engine
- **Phase 3**: Unified notification pipeline for both admission news and deadlines

**Benefits**:
- Unified notification pipeline
- Shared duplicate detection
- Single database for all content
- Flexible scheduling options

## 📈 Future Enhancements

* **Web Dashboard**: Real-time monitoring status
* **Email Notifications**: Alternative to Telegram
* **REST API**: External integrations
* **Advanced Filtering**: 지역, 전형별, 모집인원
* **Mobile App**: Push notifications
* **Multi-language Support**: English/Korean interface
* **RSS Feed Support**: Monitor university RSS feeds
* **Automated Deadline Updates**: Scrape deadline information

## 🤝 Contributing

1. **Read** `SCRAPER_DEVELOPMENT_GUIDE.md` first!
2. **Use** `scrapers/scraper_template.py` for new scrapers
3. **Test** thoroughly before submitting
4. **Document** any new patterns discovered

### Contribution Guidelines
* **New scrapers**: Follow `scraper_template.py` structure
* **Department keywords**: Add to `config/filters.yaml`
* **Testing**: Test with `python core/monitor_engine.py --test` before submitting
* **Documentation**: Update README with new source information

## 📖 Documentation

- **SCRAPER_DEVELOPMENT_GUIDE.md** - Critical patterns and solutions for scraper development
- **scrapers/scraper_template.py** - Comprehensive template with examples
- **config/** - YAML configuration examples
- **DEADLINE_INTEGRATION_PLAN.md** - Plan for integrating deadline tracking

## 📄 License

MIT License

---

**Last Updated**: 08 February 2026  
**Maintainer**: tantry  
**Status**: ✅ Production Ready (Admission Scraper Working)  
**Next Phase**: Deadline System Integration & RSS Sources  
**GitHub**: https://github.com/tantry/uni_monitoring.kr
