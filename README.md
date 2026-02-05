# University Admission Monitor (한국어: 대학 입학 모니터링 시스템)

A Python-based monitoring system that scrapes Korean university admission announcements from various sources and sends Telegram alerts for new programs across multiple departments.

## ✨ Features

- **Multi-Source Monitoring**: Scrapes admission announcements from Korean education portals
- **Multi-Department Tracking**: Monitors announcements for:
  - **Music Departments** (음악, 실용음악, 성악, 작곡)
  - **Korean Departments** (한국어, 국어국문, 국문학)
  - **English Departments** (영어, 영어영문, 영문학)
  - **Liberal Arts** (인문, 인문학, 교양교육)
- **Real-time Alerts**: Sends Telegram notifications for new admission announcements
- **Intelligent Filtering**: Filters out irrelevant content using keyword matching
- **Duplicate Detection**: Prevents duplicate alerts using content hashing
- **Modular Architecture**: Easily extensible with new data sources

## 📋 Prerequisites

- Python 3.8+
- Telegram Bot Token (from [@BotFather](https://t.me/botfather))
- Telegram Channel/Chat ID

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
1. Create a Telegram bot via [@BotFather](https://t.me/botfather)
2. Get your `BOT_TOKEN`
3. Create a channel/group and get its `CHAT_ID`
4. Add the bot as an admin to your channel

### 4. Set Up Configuration
Copy `config.example.py` to `config.py`:
```bash
cp config.example.py config.py
```

Edit `config.py` with your credentials:
```python
BOT_TOKEN = "YOUR_BOT_TOKEN_HERE"
CHAT_ID = "YOUR_CHANNEL_CHAT_ID_HERE"  # Format: -1001234567890 for channels
```

### 5. Run the Monitor
```bash
python multi_monitor.py
```

For periodic monitoring, use the included script:
```bash
./check_now.sh
```

## 🏗️ Project Structure

```
uni_monitoring.kr/
├── multi_monitor.py          # Main monitoring orchestrator
├── config.example.py         # Configuration template
├── filters.py               # Department filtering logic
├── telegram_formatter.py    # Telegram message formatting
├── check_now.sh             # Monitoring script
├── sources.py               # Source configurations
├── scrapers/               # Scraper implementations
│   ├── adiga_scraper.py    # Adiga.kr scraper (currently active)
│   ├── scraper_base.py     # Base scraper class
│   └── __init__.py
├── state.json              # Tracked articles (auto-generated)
├── .gitignore             # Security: excludes tokens and secrets
└── README.md              # This file
```

## 🔧 Configuration

### Adding New Departments
Edit `filters.py` to add new department keywords:
```python
DEPARTMENT_KEYWORDS = {
    'music': ['음악', 'music', '실용음악', '성악', '작곡'],
    'korean': ['한국어', '국어', '국어국문', '국문학'],
    'english': ['영어', '영어영문', '영문학'],
    'liberal': ['인문', '인문학', '교양', '교양교육'],
    # Add new departments here
    # 'new_dept': ['keyword1', 'keyword2', 'keyword3']
}
```

### Adding New Scrapers
1. Create a new scraper in `scrapers/` following `scraper_base.py`
2. Add source configuration in `sources.py`
3. Import and initialize in `multi_monitor.py`

## 📊 Current Data Sources

- **Adiga (어디가)**: Korean university admission news portal
  - URL: https://adiga.kr
  - Status: ✅ Active
  - Coverage: General admission news and announcements

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
   - Check `BOT_TOKEN` and `CHAT_ID` in `config.py`
   - Verify bot has admin permissions in channel
   - Check if announcements match department filters

2. **No articles found**
   - Check scraper connectivity
   - Verify department keywords match actual announcements
   - Adjust filtering strictness in `filters.py`

3. **Duplicate alerts**
   - System uses content hashing to detect duplicates
   - Check `state.json` for tracking history

4. **URL gives 404**
   - Adiga.kr may require session cookies
   - Articles use JavaScript navigation (`fnDetailPopup()`)
   - Consider using main site URL as fallback

### Debug Mode
Run with verbose output:
```bash
python multi_monitor.py 2>&1 | grep -i "filtered\|kept\|telegram\|error"
```

## 📈 Future Enhancements

- Web dashboard for monitoring status
- Email notifications as alternative to Telegram
- More data sources (각 대학교 입학처 직접 스크래핑)
- Advanced filtering (지역, 전형별, 모집인원)
- Database integration for long-term tracking
- REST API for external integrations

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Add your scraper or improvements
4. Submit a pull request

### Development Notes
- Follow the `scraper_base.py` interface for new scrapers
- Add department keywords to `filters.py`
- Test with `python test_integration.py` before submitting

## 📄 License

MIT License - see LICENSE file for details

## 🙏 Acknowledgements

- Built for Korean university admission monitoring community
- Uses BeautifulSoup for web scraping
- Telegram Bot API for notifications
- Community contributors for scraper implementations

---

**Last Updated**: 05 February 2026  
**Active Development**: Yes  
**Primary Maintainer**: tantry  
**Telegram Support**: @ReiUniMonitor_bot (KR Uni Monitor)
```

## 🎯 **Key updates I made:**

1. **Current Status**: Reflects the actual working system with Adiga scraper
2. **Telegram Format**: Shows actual message format with HTML
3. **URL Pattern**: Updated to show `ArticleDetail.do?articleID=` format
4. **GitHub Integration**: Added section about secure push scripts
5. **Troubleshooting**: Added specific solutions for 404 URLs and JavaScript navigation
6. **Structure**: Updated to match your actual file structure
7. **Security**: Emphasized `.gitignore` protection for tokens
8. **Acknowledgements**: Added your Telegram bot info
