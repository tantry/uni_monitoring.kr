```markdown
# University Admission Monitor (한국어: 대학 입학 모니터링 시스템)

A Python-based monitoring system that scrapes Korean university admission announcements from various sources and sends Telegram alerts for new programs across multiple departments.

## ✨ Features

- **Multi-Source Monitoring**: Scrapes admission announcements from various Korean education portals
- **Multi-Department Tracking**: Monitors announcements for:
  - **Music Departments** (음악, 실용음악, 성악, 작곡)
  - **Korean Departments** (한국어, 국어국문, 국문학)
  - **English Departments** (영어, 영어영문, 영문학)
  - **Liberal Arts** (인문, 인문학, 교양교육)
- **Real-time Alerts**: Sends Telegram notifications for new admission announcements
- **Intelligent Filtering**: Filters out irrelevant content using keyword matching
- **Duplicate Detection**: Prevents duplicate alerts using content hashing
- **Multi-Scraper Architecture**: Easily extensible with new data sources

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
├── multi_monitor.py          # Main monitoring script
├── config.py                # Configuration (BOT_TOKEN, CHAT_ID)
├── filters.py               # Department filtering logic
├── check_now.sh             # Monitoring script
├── sources.py               # Source configurations
├── scrapers/               # Scraper implementations
│   ├── adiga_scraper.py    # Adiga.kr scraper
│   ├── scraper_base.py     # Base scraper class
│   └── __init__.py
└── README.md
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
- *More sources can be added easily*

## 🤖 Telegram Integration

The system sends formatted Telegram messages:

```
🎓 [새 입학 공고] 서울대학교 음악학과

📌 프로그램: 음악학과 추가모집
🏫 대학교: 서울대학교
📅 마감일: 2024.12.20
🔗 링크: https://example.com/admission

📋 키워드: 음악, 추가모집, 입시
📍 지역: 서울
```

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

### Debug Mode
Run with verbose output:
```bash
python multi_monitor.py 2>&1 | grep -i "filtered\|kept\|telegram"
```

## 📈 Future Enhancements

- [ ] Web dashboard for monitoring status
- [ ] Email notifications
- [ ] More data sources (각 대학교 입학처)
- [ ] Advanced filtering (지역, 전형별)
- [ ] Database integration for long-term tracking

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Add your scraper or improvements
4. Submit a pull request

## 📄 License

MIT License - see LICENSE file for details

## 🙏 Acknowledgements

- Built for Korean university admission monitoring
- Uses BeautifulSoup for web scraping
- Telegram Bot API for notifications
- Community contributors for scraper implementations
```
Updated: 2026-02-05
## Key Changes to README:
1. **Updated feature description** from "music admission" to "multiple departments"
2. **Added department list** showing all tracked departments
3. **Updated configuration instructions** to reflect current system
4. **Added department configuration section** showing how to add new departments
5. **Updated troubleshooting** for multi-department filtering
6. **Updated Telegram message example** to show department information

The README now accurately reflects that your system monitors **Music, Korean, English, and Liberal Arts departments** (with easy expansion to more departments).
