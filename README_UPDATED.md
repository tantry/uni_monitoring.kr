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
* **Duplicate Detection**: Prevents duplicate alerts using SQLite database
* **Modular Architecture**: Easily extensible with new data sources
* **Safe GitHub Integration**: Interactive push scripts with review steps

## 📋 Current Project Structure

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
│   ├── article.py             # Article data class (Pydantic model)
│   └── __init__.py
├── scrapers/                  # Scraper implementations
│   ├── adiga_scraper.py       # Adiga.kr scraper (active)
│   ├── scraper_base.py        # Legacy base scraper (deprecated)
│   ├── scraper_template.py    # Template for new scrapers (NEW)
│   └── __init__.py
├── notifiers/                 # Notification systems
│   ├── telegram_notifier.py   # Telegram notification handler
│   └── __init__.py
├── filters/                   # Filter implementations
│   ├── department_filter.py   # Department-based filtering
│   └── __init__.py
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
├── check_now.sh               # Monitoring script
└── README.md                  # This file
```

## 🚀 Quick Start

### 1. Clone the Repository

    git clone https://github.com/tantry/uni_monitoring.kr.git
    cd uni_monitoring.kr

### 2. Install Dependencies

    pip install -r requirements.txt

### 3. Configure Telegram

1. Create a Telegram bot via @BotFather
2. Get your `BOT_TOKEN`
3. Create a channel/group and get its `CHAT_ID`
4. Add the bot as an admin to your channel

### 4. Set Up Configuration

Copy the example configuration files:

    cp config/config.example.yaml config/config.yaml
    cp config/sources.example.yaml config/sources.yaml
    cp config/filters.example.yaml config/filters.yaml

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

### 5. Set Up GitHub (Optional)

For safe GitHub pushes:

    ./setup_github_safe.sh

### 6. Run the Monitor

**New architecture mode:**

    python core/monitor_engine.py

**Test mode (no notifications):**

    python core/monitor_engine.py --test

**Legacy mode (for backward compatibility):**

    python multi_monitor.py

For periodic monitoring, use the included script:

    ./check_now.sh

## 🏗️ Scraper Development

### Creating New Scrapers

Use the template to create new scrapers:

    cp scrapers/scraper_template.py scrapers/new_source_scraper.py

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
        """
        Fetch articles from the source.
        
        Returns:
            List of dictionaries with raw article data
        """
        articles = []
        
        try:
            # 1. Fetch the page
            # 2. Parse HTML/JSON
            # 3. Extract article information
            # 4. Return list of articles
            
            # Example structure for each article:
            # {
            #     'title': 'Article Title',
            #     'url': 'https://example.com/article/123',
            #     'content': 'Article content or preview',
            #     'source': self.source_name,
            #     'published_date': '2026-02-07',
            # }
            
            pass
            
        except Exception as e:
            logger.error(f"Error fetching articles from {self.source_name}: {e}")
        
        return articles
    
    def parse_article(self, raw_data: Dict) -> Article:
        """
        Parse raw article data into Article model.
        
        Args:
            raw_data: Dictionary with raw article data
            
        Returns:
            Article object
        """
        try:
            article = Article(
                title=raw_data.get('title', ''),
                url=raw_data.get('url', ''),
                content=raw_data.get('content', ''),
                source=raw_data.get('source', self.source_name),
                published_date=raw_data.get('published_date'),
                department=self.detect_department(raw_data)
            )
            return article
            
        except Exception as e:
            logger.error(f"Error parsing article: {e}")
            return self.create_error_article(raw_data)
    
    def get_source_name(self) -> str:
        return self.source_name
    
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

## 📊 Current Data Sources

### Adiga (어디가)
* **URL**: https://www.adiga.kr
* **Status**: 🔧 Active (Requires Content Discovery)
* **Coverage**: General admission news and announcements
* **Current Issue**: `prtlBbsId` URLs point to privacy policies, not admission content
* **Next Steps**: Discover actual admission announcement URLs

### Target Universities for Future Development
1. **서울대학교** - https://admission.snu.ac.kr
2. **연세대학교** - https://admission.yonsei.ac.kr  
3. **고려대학교** - https://admission.korea.ac.kr
4. **한국대학교** - Individual department pages

## 🤖 Telegram Integration

The system sends formatted Telegram messages:

```
🎵 [새 입학 공고] 서울대학교 음악학과 추가모집

📌 부서/학과: music
📝 내용: 서울대학교 음악학과에서 2026학년도 추가모집을 실시합니다...
🔗 링크: https://adiga.kr/ArticleDetail.do?articleID=26546

#대학입시 #music
```

## 🔄 GitHub Integration

### Safe Push System

The repository includes safe scripts for GitHub integration:

**Setup (one-time):**

    ./setup_github_safe.sh

**Safe Push (interactive):**

    ./push_to_github_safe.sh

**Original Push (automatic):**

    ./push_to_github.sh

**Security Note**: All tokens and credentials are automatically excluded via `.gitignore`.

## 🎯 Architecture Status

### ✅ Completed Foundation
* **New Core Architecture**: `core/base_scraper.py`, `core/filter_engine.py`, `core/scraper_factory.py`
* **Enhanced Configuration**: YAML-based configs in `config/` directory
* **Data Models**: `models/article.py` for standardized article representation
* **State Management**: SQLite database for reliable state tracking
* **Safe GitHub Integration**: Interactive push scripts with review steps

### 🔄 In Progress
* **Scraper Migration**: Migrating `scrapers/adiga_scraper.py` to use new architecture
* **Content Discovery**: Finding actual admission announcement URLs on Adiga.kr
* **Template System**: Creating reusable scraper templates

### 📋 Pending
* **Additional Sources**: Implementing scrapers for target universities
* **Testing Framework**: Comprehensive test suite
* **Web Dashboard**: Monitoring status interface

## 🐛 Troubleshooting

### Common Issues

1. **No Telegram alerts**
   * Check `BOT_TOKEN` and `CHAT_ID` in `config/config.yaml`
   * Verify bot has admin permissions in channel
   * Check if announcements match department filters
   * Check logs in `logs/monitor.log` for errors

2. **No articles found**
   * Current Adiga implementation finds privacy policy pages, not admission content
   * Need to discover actual admission announcement URLs
   * Consider implementing alternative sources

3. **Duplicate alerts**
   * System uses SQLite database for duplicate detection
   * Check `data/state.db` for tracking history

4. **GitHub push issues**
   * Use `./setup_github_safe.sh` to configure properly
   * `./push_to_github_safe.sh` provides interactive review

### Debug Mode

Run with verbose output:

    python core/monitor_engine.py --verbose

Or check the logs:

    tail -f logs/monitor.log

## 🚧 Development Guide

### For New Contributors

1. **Start with the template**: `scrapers/scraper_template.py`
2. **Test locally**: `python scrapers/your_scraper.py`
3. **Integrate**: Add to `config/sources.yaml` and `core/scraper_factory.py`
4. **Test with monitor**: `python core/monitor_engine.py --test`

### Testing New Sources

1. Create test script:

```python
# test_new_source.py
import sys
sys.path.insert(0, '.')
from scrapers.your_scraper import YourScraper

scraper = YourScraper({})
articles = scraper.fetch_articles()
print(f"Found {len(articles)} articles")
for article in articles[:5]:
    print(f"• {article.get('title', 'No title')}")
    print(f"  URL: {article.get('url', 'No URL')}")
```

2. Run test:

    python test_new_source.py

## 📈 Future Enhancements

* **Web Dashboard**: Real-time monitoring status
* **Email Notifications**: Alternative to Telegram
* **REST API**: External integrations
* **Advanced Filtering**: 지역, 전형별, 모집인원
* **Mobile App**: Push notifications
* **Multi-language Support**: English/Korean interface

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Add your scraper using the template
4. Test thoroughly
5. Submit a pull request

### Contribution Guidelines

* **New scrapers**: Follow `scraper_template.py` structure
* **Department keywords**: Add to `config/filters.yaml`
* **Testing**: Test with `python core/monitor_engine.py --test` before submitting
* **Documentation**: Update README with new source information

## 📄 License

MIT License - see LICENSE file for details

## 🙏 Acknowledgements

* Built for Korean university admission monitoring community
* Uses BeautifulSoup for web scraping
* Telegram Bot API for notifications
* Community contributors for scraper implementations

---

**Last Updated**: 07 February 2026  
**Active Development**: Yes (Content Discovery in Progress)  
**Primary Maintainer**: tantry  
**GitHub**: https://github.com/tantry/uni_monitoring.kr  
**Architecture Status**: ✅ Foundation Complete, 🔄 Scraper Content Discovery Needed
