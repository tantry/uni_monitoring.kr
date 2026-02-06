
I've created a comprehensive future project plan that includes:

## **What's in the FUTURE_PROJECTS.md file:**

1. **Complete roadmap** for multi-site aggregation
2. **5 target sites** with specific features to monitor
3. **Technical architecture** with database design
4. **Module structure** for scalable development
5. **Implementation roadmap** with 5 phases
6. **Challenges and solutions**
7. **Priority features** categorized
8. **Technology stack** recommendations
9. **Success metrics** to track
10. **Quick start guide** for when you're ready

## **Next Steps for Current Project:**

1. First, let's fix the Adiga link issue (Phase 2)
2. Then set up systemd/cron for automation (Phase 3)
3. When ready, refer to `FUTURE_PROJECTS.md` to start Phase 4

## **To view the plan:**

```bash
cd ~/uni_monitoring
cat FUTURE_PROJECTS.md

Priority when suggesting fixes: ensure a robust architecture to allow for the objectives of the project.. allowing for easy filter adjustments, additions of new scrapers.
no quick fixes, i want to build the robust architecture - there is no priority to have a working system in a very short time

🏗️ Robust Architecture Design
1. Directory Structure


uni_monitoring.kr/
├── config/                    # Configuration files
│   ├── sources.yaml          # Source definitions
│   ├── filters.yaml          # Department filters  
│   └── telegram.yaml         # Notification settings
├── core/                     # Core framework
│   ├── __init__.py
│   ├── base_scraper.py      # Abstract base class
│   ├── scraper_factory.py   # Factory pattern
│   ├── filter_engine.py     # Filtering system
│   ├── notifier.py          # Notification system
│   └── storage.py           # Data persistence
├── scrapers/                 # Individual scrapers
│   ├── __init__.py
│   ├── adiga_scraper.py     # Adiga implementation
│   └── base_scraper.py      # (symlink to core/base_scraper.py)
├── models/                   # Data models
│   ├── __init__.py
│   ├── article.py           # Article data model
│   └── university.py        # University/department models
├── utils/                    # Utilities
│   ├── __init__.py
│   ├── logger.py            # Logging setup
│   └── validators.py        # Data validation
├── tests/                    # Test suite
│   ├── __init__.py
│   ├── test_scrapers.py
│   └── test_filters.py
├── scripts/                  # Maintenance scripts
│   ├── add_scraper.py       # Interactive scraper creator
│   └── update_filters.py    # Filter management
└── main.py                   # Entry point


2. Core Components
A. Configuration System (YAML-based)

# config/sources.yaml
sources:
  adiga:
    name: "Adiga (어디가)"
    enabled: true
    base_url: "https://adiga.kr"
    scraper_class: "AdigaScraper"
    schedule: "*/30 * * * *"  # Every 30 minutes
    priority: 1
    timeout: 30
    retry_attempts: 3
    
  example_university:
    name: "Example University"
    enabled: false  # Not yet implemented
    base_url: "https://admission.example.ac.kr"
    scraper_class: "ExampleScraper"
    schedule: "0 9,15 * * *"  # 9AM and 3PM daily

# config/filters.yaml
departments:
  music:
    name: "음악학과"
    keywords: ["음악", "music", "실용음악", "성악", "작곡"]
    emoji: "🎵"
    priority: 1
    
  korean:
    name: "국어국문학과" 
    keywords: ["한국어", "국어", "국어국문", "국문학"]
    emoji: "📚"
    priority: 2
    
  english:
    name: "영어영문학과"
    keywords: ["영어", "영어영문", "영문학", "영미문학"]
    emoji: "🔤"
    priority: 3

# Add new department:
# 1. Add entry here
# 2. System auto-detects on next run


B. Base Scraper Abstract Class

# core/base_scraper.py
from abc import ABC, abstractmethod
from datetime import datetime
from typing import List, Dict, Optional
import hashlib
import json
from pathlib import Path

class BaseScraper(ABC):
    """Abstract base class for all university admission scrapers"""
    
    def __init__(self, config: Dict):
        self.config = config
        self.name = config['name']
        self.base_url = config['base_url']
        self.logger = self._setup_logger()
        self.storage_path = Path(f"data/{self.name}")
        self.storage_path.mkdir(parents=True, exist_ok=True)
        
    @abstractmethod
    def fetch_articles(self) -> List['Article']:
        """Fetch raw articles from source - MUST be implemented"""
        pass
    
    @abstractmethod
    def parse_article(self, raw_data) -> 'Article':
        """Parse raw data into Article model - MUST be implemented"""
        pass
    
    def generate_id(self, article: 'Article') -> str:
        """Generate unique ID for article (override if needed)"""
        content = f"{article.title}{article.url}{article.published_date}"
        return hashlib.md5(content.encode()).hexdigest()
    
    def save_state(self, articles: List['Article']):
        """Save scraped articles to JSON file"""
        state_file = self.storage_path / f"state_{datetime.now().date()}.json"
        data = {
            'scraped_at': datetime.now().isoformat(),
            'source': self.name,
            'articles': [article.to_dict() for article in articles]
        }
        state_file.write_text(json.dumps(data, indent=2, ensure_ascii=False))
    
    def load_previous_state(self) -> List['Article']:
        """Load previous state for duplicate detection"""
        # Implement state management
        pass
    
    def find_new_articles(self, current: List['Article']) -> List['Article']:
        """Compare with previous state to find new articles"""
        previous = self.load_previous_state()
        previous_ids = {article.id for article in previous}
        return [article for article in current if article.id not in previous_ids]
        
        
        
C. Article Data Model

# models/article.py
from dataclasses import dataclass, asdict
from datetime import datetime
from typing import Optional, Dict, Any
from enum import Enum

class ArticleStatus(Enum):
    NEW = "new"
    PROCESSED = "processed"
    SENT = "sent"
    ERROR = "error"

@dataclass
class Article:
    """Unified article data model"""
    id: str
    title: str
    content: str
    url: str
    source: str
    published_date: Optional[datetime] = None
    department: Optional[str] = None
    university: Optional[str] = None
    deadline: Optional[datetime] = None
    metadata: Dict[str, Any] = None
    status: ArticleStatus = ArticleStatus.NEW
    created_at: datetime = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()
        if self.metadata is None:
            self.metadata = {}
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON serialization"""
        data = asdict(self)
        # Handle datetime serialization
        for key, value in data.items():
            if isinstance(value, datetime):
                data[key] = value.isoformat()
            elif isinstance(value, ArticleStatus):
                data[key] = value.value
        return data
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Article':
        """Create Article from dictionary"""
        # Handle datetime deserialization
        if 'published_date' in data and data['published_date']:
            data['published_date'] = datetime.fromisoformat(data['published_date'])
        if 'deadline' in data and data['deadline']:
            data['deadline'] = datetime.fromisoformat(data['deadline'])
        if 'created_at' in data:
            data['created_at'] = datetime.fromisoformat(data['created_at'])
        if 'status' in data:
            data['status'] = ArticleStatus(data['status'])
        return cls(**data)
        
        
D. Filter Engine

# core/filter_engine.py
import yaml
from typing import List, Optional, Dict
from pathlib import Path

class FilterEngine:
    """Dynamic department filtering system"""
    
    def __init__(self, config_path: str = "config/filters.yaml"):
        self.config_path = Path(config_path)
        self.departments = self._load_departments()
        self._setup_watcher()  # Watch for config changes
        
    def _load_departments(self) -> Dict:
        """Load department configuration from YAML"""
        if not self.config_path.exists():
            return self._create_default_config()
        
        with open(self.config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        
        return config.get('departments', {})
    
    def detect_department(self, article_text: str) -> Optional[str]:
        """Detect which department an article belongs to"""
        text_lower = article_text.lower()
        
        for dept_id, dept_config in self.departments.items():
            keywords = dept_config.get('keywords', [])
            for keyword in keywords:
                if keyword.lower() in text_lower:
                    return dept_id
        
        return None
    
    def add_department(self, dept_id: str, name: str, keywords: List[str], emoji: str = "🎓"):
        """Add new department at runtime"""
        self.departments[dept_id] = {
            'name': name,
            'keywords': keywords,
            'emoji': emoji
        }
        self._save_config()
        return True
    
    def _save_config(self):
        """Save current configuration to YAML"""
        config = {'departments': self.departments}
        with open(self.config_path, 'w', encoding='utf-8') as f:
            yaml.dump(config, f, allow_unicode=True, sort_keys=False)
    
    def get_department_info(self, dept_id: str) -> Dict:
        """Get department configuration"""
        return self.departments.get(dept_id, {})
    
    
E. Scraper Factory

# core/scraper_factory.py
import importlib
from typing import Dict, Type
from pathlib import Path
import yaml

from .base_scraper import BaseScraper

class ScraperFactory:
    """Factory for creating scraper instances"""
    
    def __init__(self, config_dir: str = "config"):
        self.config_dir = Path(config_dir)
        self.sources_config = self._load_config('sources.yaml')
        self._scraper_cache = {}  # Cache instantiated scrapers
        
    def _load_config(self, filename: str) -> Dict:
        """Load configuration from YAML file"""
        config_path = self.config_dir / filename
        if not config_path.exists():
            raise FileNotFoundError(f"Config file not found: {config_path}")
        
        with open(config_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    
    def get_enabled_sources(self) -> List[str]:
        """Get list of enabled source IDs"""
        sources = self.sources_config.get('sources', {})
        return [source_id for source_id, config in sources.items() 
                if config.get('enabled', False)]
    
    def create_scraper(self, source_id: str) -> BaseScraper:
        """Create scraper instance for given source"""
        if source_id in self._scraper_cache:
            return self._scraper_cache[source_id]
        
        source_config = self.sources_config['sources'].get(source_id)
        if not source_config:
            raise ValueError(f"Unknown source: {source_id}")
        
        # Dynamic import
        scraper_class_name = source_config['scraper_class']
        module_name = f"scrapers.{scraper_class_name.lower()}"
        
        try:
            module = importlib.import_module(module_name)
            scraper_class = getattr(module, scraper_class_name)
            
            # Instantiate with config
            scraper = scraper_class(source_config)
            self._scraper_cache[source_id] = scraper
            
            return scraper
            
        except (ImportError, AttributeError) as e:
            raise ImportError(
                f"Failed to load scraper {scraper_class_name} for {source_id}: {e}"
            )
    
    def create_all_enabled(self) -> List[BaseScraper]:
        """Create all enabled scrapers"""
        return [self.create_scraper(source_id) 
                for source_id in self.get_enabled_sources()]
                
                
3. Implementation Strategy

Phase 1: Foundation (Week 1)

    Set up the directory structure

    Implement base classes and data models

    Create configuration system (YAML)

    Migrate existing Adiga scraper to new architecture

Phase 2: Core Systems (Week 2)

    Implement filter engine with YAML config

    Build scraper factory pattern

    Create notification system with multiple channels

    Add proper logging and error handling

Phase 3: Enhancement (Week 3)

    Add database persistence (SQLite → PostgreSQL)

    Implement web dashboard

    Add API endpoints

    Create monitoring and alerting

Phase 4: Scaling (Week 4+)

    Add more university sources

    Implement distributed scraping

    Add machine learning for better filtering

    Create mobile app interface

4. Getting Started

Let me create the initial structure and migrate your Adiga scraper properly:

# Create the robust architecture structure
mkdir -p config core scrapers models utils tests scripts

# Create configuration files
cat > config/sources.yaml << 'EOF'
sources:
  adiga:
    name: "Adiga (어디가)"
    enabled: true
    base_url: "https://adiga.kr"
    scraper_class: "AdigaScraper"
    schedule: "*/30 * * * *"
    priority: 1
    timeout: 30
    retry_attempts: 3
    user_agent: "Mozilla/5.0 UniversityMonitor/1.0"
EOF

cat > config/filters.yaml << 'EOF'
departments:
  music:
    name: "음악학과"
    keywords: ["음악", "music", "실용음악", "성악", "작곡", "교향곡", "오케스트라"]
    emoji: "🎵"
    priority: 1
    
  korean:
    name: "국어국문학과"
    keywords: ["한국어", "국어", "국어국문", "국문학", "한국언어", "한글"]
    emoji: "📚"
    priority: 2
    
  english:
    name: "영어영문학과"
    keywords: ["영어", "영어영문", "영문학", "영미언어", "영미문화"]
    emoji: "🔤"
    priority: 3
    
  liberal:
    name: "인문학부"
    keywords: ["인문", "인문학", "교양", "교양교육", "자유전공", "기초교육"]
    emoji: "📖"
    priority: 4
EOF

# Would you like me to proceed with creating the core/base_scraper.py 
# and migrating your Adiga scraper to this new architecture?

This architecture gives you:

    Configurability: Add sources/filters via YAML, no code changes

    Extensibility: New scrapers just implement the interface

    Maintainability: Clear separation of concerns

    Testability: Each component can be tested independently

    Scalability: Ready for multiple sources and departments

    
    COMPLETED BY USER: Getting Started.
    Next:
    Section 
    2.A - "Base Scraper Abstract Class" and create core/base_scraper.py with the code provided there.
    2.B - models/article.py with the Article data model
    2.C - core/filter_engine.py with the FilterEngine class
    2.D - Create core/scraper_factory.py with the ScraperFactory
Then proceed to:
migrate your Adiga scraper to inherit f






















rom the new BaseScraper.
