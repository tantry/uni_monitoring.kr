# University Admission Monitor (한국어: 대학 입학 모니터링 시스템)

A Python-based monitoring system that scrapes Korean university admission announcements from various sources and sends Telegram alerts for new programs across multiple departments.

## ✨ Features

* **Multi-Source Monitoring**: Scrapes admission announcements from Korean education portals
* **Multi-Department Tracking**: Monitors announcements for:
  * **Music Departments** (음악, 실용음악, 성악, 작곡)
  * **Korean Departments** (한국어, 국어국문, 국문학)
  * **English Departments** (영어, 영어영문, 영문학)
  * **Liberal Arts** (인문, 인문학, 교양교육)
* **Real-time Alerts**: Sends Telegram notifications for new admission announcements
* **Intelligent Filtering**: Filters out irrelevant content using keyword matching
* **Duplicate Detection**: Prevents duplicate alerts using content hashing
* **Modular Architecture**: Easily extensible with new data sources
* **Robust Foundation**: Enterprise-grade architecture with proper error handling, logging, and configuration management

## 📋 Prerequisites

* Python 3.8+
* Telegram Bot Token (from @BotFather)
* Telegram Channel/Chat ID

## 🚀 Quick Start

### 1. Clone the Repository

```bash
git clone https://github.com/tantry/uni_monitoring.kr.git
cd uni_monitoring.kr
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure Telegram

1. Create a Telegram bot via @BotFather
2. Get your `BOT_TOKEN`
3. Create a channel/group and get its `CHAT_ID`
4. Add the bot as an admin to your channel

### 4. Set Up Configuration

Copy the example configuration files:

```bash
cp config/config.example.yaml config/config.yaml
cp config/sources.example.yaml config/sources.yaml
cp config/filters.example.yaml config/filters.yaml
```

Edit `config/config.yaml` with your credentials:

```yaml
telegram:
  bot_token: "YOUR_BOT_TOKEN_HERE"
  chat_id: "YOUR_CHANNEL_CHAT_ID_HERE"  # Format: -1001234567890 for channels

database:
  path: "data/state.db"  # SQLite database for state management

logging:
  level: "INFO"
  file: "logs/monitor.log"
```

### 5. Run the Monitor

**Legacy mode (for backward compatibility):**
```bash
python multi_monitor.py
```

**New architecture mode:**
```bash
python core/monitor_engine.py
```

For periodic monitoring, use the included script:
```bash
./check_now.sh
```

## 🏗️ Project Structure (Enhanced)

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
│   └── article.py             # Article data class
├── scrapers/                  # Scraper implementations
│   ├── adiga_scraper.py       # Adiga.kr scraper (migrating to new architecture)
│   ├── scraper_base.py        # Legacy base scraper (deprecated)
│   └── __init__.py
├── notifiers/                 # Notification systems
│   ├── telegram_notifier.py   # Telegram notification handler
│   └── __init__.py
├── filters/                   # Filter implementations
│   ├── department_filter.py   # Department-based filtering
│   └── __init__.py
├── data/                      # Data storage
│   └── state.db               # SQLite database (auto-generated)
├── logs/                      # Log files
│   └── monitor.log            # Application logs (auto-generated)
├── multi_monitor.py           # Legacy monitoring orchestrator
├── filters.py                 # Legacy filtering logic
├── telegram_formatter.py      # Legacy Telegram formatter
├── check_now.sh               # Monitoring script
├── state.json                 # Legacy state tracking (auto-generated)
└── README.md                  # This file
```

## 🎯 Architecture Migration Status

### ✅ Completed Foundation
- **New Core Architecture**: `core/base_scraper.py`, `core/filter_engine.py`, `core/scraper_factory.py`
- **Enhanced Configuration**: YAML-based configs in `config/` directory
- **Data Models**: `models/article.py` for standardized article representation
- **State Management**: SQLite database for reliable state tracking

### 🔄 In Progress
- **Scraper Migration**: Migrating `scrapers/adiga_scraper.py` to inherit from new `BaseScraper`
- **Legacy Integration**: Maintaining backward compatibility during transition

### 📋 Pending
- **Notification System**: Migrating to new `notifiers/` architecture
- **Testing Framework**: Comprehensive test suite for new architecture
- **Documentation**: API documentation and contributor guidelines

## 🔧 Configuration

### Adding New Departments

Edit `config/filters.yaml` to add new department keywords:

```yaml
departments:
  music:
    keywords: ['음악', 'music', '실용음악', '성악', '작곡']
    description: "Music related departments"
  korean:
    keywords: ['한국어', '국어', '국어국문', '국문학']
    description: "Korean language departments"
  english:
    keywords: ['영어', '영어영문', '영문학']
    description: "English language departments"
  liberal:
    keywords: ['인문', '인문학', '교양', '교양교육']
    description: "Liberal arts departments"
  
  # Add new departments here:
  # new_dept:
  #   keywords: ['keyword1', 'keyword2', 'keyword3']
  #   description: "Description of new department"
```

### Adding New Scrapers (New Architecture)

1. Create a new scraper in `scrapers/` inheriting from `BaseScraper`
2. Add source configuration in `config/sources.yaml`
3. Register the scraper in `core/scraper_factory.py`
4. Test with the new monitoring engine

### Adding New Scrapers (Legacy Architecture)

1. Create a new scraper in `scrapers/` following `scraper_base.py`
2. Add source configuration in `sources.py`
3. Import and initialize in `multi_monitor.py`

## 📊 Current Data Sources

* **Adiga (어디가)**: Korean university admission news portal
  * URL: https://adiga.kr
  * Status: ✅ Active (Legacy), 🔄 Migrating to New Architecture
  * Coverage: General admission news and announcements

*More sources can be added easily through the modular scraper system*

## 🤖 Telegram Integration

The system sends formatted Telegram messages with HTML formatting:

```
🎵 [새 입학 공고] 서울대학교 음악학과 추가모집

📌 부서/학과: music
📝 내용: 서울대학교 음악학과에서 2026학년도 추가모집을 실시합니다...
🔗 링크: https://adiga.kr/ArticleDetail.do?articleID=26546

#대학입시 #music
```

## 🔄 GitHub Integration

### Secure Push Scripts

The repository includes secure scripts for automated GitHub pushes:

```bash
# Setup (one-time)
./setup_github.sh

# Manual push
./push_to_github.sh

# Automated daily push
./daily_push.sh
```

**Security Note**: All tokens and credentials are automatically excluded via `.gitignore`.

## 🐛 Troubleshooting

### Common Issues

1. **No Telegram alerts**
   * Check `BOT_TOKEN` and `CHAT_ID` in `config/config.yaml`
   * Verify bot has admin permissions in channel
   * Check if announcements match department filters
   * Check logs in `logs/monitor.log` for errors

2. **No articles found**
   * Check scraper connectivity
   * Verify department keywords match actual announcements
   * Adjust filtering strictness in `config/filters.yaml`

3. **Duplicate alerts**
   * System uses database-backed duplicate detection
   * Check `data/state.db` for tracking history

4. **URL gives 404**
   * Adiga.kr may require session cookies
   * Articles use JavaScript navigation (`fnDetailPopup()`)
   * Consider using main site URL as fallback

### Debug Mode

Run with verbose output:

```bash
python core/monitor_engine.py --verbose
```

Or check the logs:

```bash
tail -f logs/monitor.log
```

## 🚧 Migration Guide

### For Developers: Migrating Legacy Scrapers

To migrate an existing scraper to the new architecture:

1. **Update scraper class** to inherit from `BaseScraper` instead of `ScraperBase`
2. **Implement required methods**:
   - `fetch_articles()`: Fetch raw articles from source
   - `parse_article()`: Parse raw data into `Article` model
   - `get_source_name()`: Return unique source identifier
3. **Update configuration** in `config/sources.yaml`
4. **Test** with the new monitoring engine

Example migration template:

```python
from core.base_scraper import BaseScraper
from models.article import Article

class NewAdigaScraper(BaseScraper):
    def __init__(self, config):
        super().__init__(config)
        self.base_url = "https://adiga.kr"
    
    def fetch_articles(self):
        # Implementation here
        pass
    
    def parse_article(self, raw_data):
        # Implementation here
        pass
    
    def get_source_name(self):
        return "adiga"
```

### For Users: Transition Period

During the migration period, both systems will work in parallel:
- **Legacy system**: `multi_monitor.py` → Uses `state.json`
- **New system**: `core/monitor_engine.py` → Uses `data/state.db`

## 📈 Future Enhancements

* Web dashboard for monitoring status
* Email notifications as alternative to Telegram
* More data sources (각 대학교 입학처 직접 스크래핑)
* Advanced filtering (지역, 전형별, 모집인원)
* REST API for external integrations
* Containerization with Docker

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Add your scraper or improvements
4. Submit a pull request

### Development Notes

* **New contributions**: Follow the `core/base_scraper.py` interface
* **Maintenance contributions**: Follow existing patterns during transition
* **Department keywords**: Add to `config/filters.yaml`
* **Testing**: Test with `python test_integration.py` before submitting

## 📄 License

MIT License - see LICENSE file for details

## 🙏 Acknowledgements

* Built for Korean university admission monitoring community
* Uses BeautifulSoup for web scraping
* Telegram Bot API for notifications
* Community contributors for scraper implementations

---

**Last Updated**: 06 February 2026  
**Active Development**: Yes (Architecture Migration in Progress)  
**Primary Maintainer**: tantry  
**Telegram Support**: @ReiUniMonitor_bot (KR Uni Monitor)  
**Architecture Status**: ✅ Foundation Built, 🔄 Scraper Migration in Progress
```

## Key Changes Made to README:

1. **Architecture Status Section**: Clearly shows what's completed (✅), in progress (🔄), and pending (📋)
2. **Updated Project Structure**: Reflects the new robust architecture you've built
3. **Migration Guide**: Separate section for developers migrating scrapers
4. **Transition Period**: Explains how both legacy and new systems work during migration
5. **Configuration Updates**: Shows YAML-based config instead of Python files
6. **Clear Path Forward**: Guides users on next steps for the migration
