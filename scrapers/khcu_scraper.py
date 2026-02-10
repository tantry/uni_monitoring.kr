"""
KHCU Scraper with Advanced Multi-Filter Implementation
Includes: Department filters, Item type filters, Exclusion patterns
Threshold: 0.10 (10% keyword match confidence)
"""

import logging
import re
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timedelta
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options

try:
    from core.base_scraper import BaseScraper
    from models.article import Article
except ImportError:
    class BaseScraper:
        def __init__(self, config):
            self.config = config
            self.logger = logging.getLogger(self.__class__.__name__)
    
    class Article:
        def __init__(self, **kwargs):
            self.__dict__.update(kwargs)


logger = logging.getLogger(__name__)


class FilterConfig:
    """Advanced filter configuration"""
    
    CONFIDENCE_THRESHOLD = 0.10  # 10% keyword match
    
    # Department keywords (your interests)
    DEPARTMENTS = {
        'taxation_accounting': {
            'korean': ['세무', '회계', '세무회계', '세무회계학부'],
            'english': ['taxation', 'accounting', 'tax', 'audit'],
        },
        'finance_insurance': {
            'korean': ['금융', '보험', '금융보험', '금융보험학부'],
            'english': ['finance', 'insurance', 'banking', 'financial'],
        },
        'business_admin': {
            'korean': ['경영', '경영학', '경영학부', '경영정보'],
            'english': ['business', 'management', 'administration'],
        }
    }
    
    # Item type keywords
    ITEM_TYPES = {
        'admission': {
            'korean': ['입학', '입시', '모집', '수시', '정시', '편입'],
            'english': ['admission', 'enrollment', 'recruitment', 'entrance'],
            'priority': 1
        },
        'exam': {
            'korean': ['시험', '고사', '중간고사', '기말고사', '평가'],
            'english': ['exam', 'test', 'midterm', 'final', 'assessment'],
            'priority': 2
        },
        'registration': {
            'korean': ['등록', '신청', '수강신청', '수강변경', '등록금'],
            'english': ['registration', 'enrollment', 'course selection'],
            'priority': 3
        }
    }
    
    # Exclude patterns (items to filter OUT)
    EXCLUDE = {
        'closures': {
            'korean': ['휴무', '폐쇄', '운영중단', '휴일'],
            'english': ['closed', 'closure', 'shutdown', 'holiday'],
        },
        'expired': {
            'korean': ['만료', '종료', '완료', '마감'],
            'english': ['expired', 'ended', 'completed', 'deadline'],
        }
    }


class KhcuScraperAdvanced(BaseScraper):
    """KHCU Scraper with advanced multi-filter implementation"""
    
    def __init__(self, config: dict):
        super().__init__(config)
        self.base_url = "https://khcu.ac.kr"
        self.schedule_url = f"{self.base_url}/schedule/index.do"
        self.source_name = "khcu"
        self.driver = None
        
        # Date filtering
        self.date_filter_days = config.get('date_filter_days', 120)
        
        # Advanced filtering
        self.enable_department_filter = config.get('enable_department_filter', True)
        self.enable_item_type_filter = config.get('enable_item_type_filter', True)
        self.enable_exclude_filter = config.get('enable_exclude_filter', True)
        self.confidence_threshold = config.get('confidence_threshold', FilterConfig.CONFIDENCE_THRESHOLD)
        
        self.logger.info(f"Filtering enabled:")
        self.logger.info(f"  - Department: {self.enable_department_filter}")
        self.logger.info(f"  - Item Type: {self.enable_item_type_filter}")
        self.logger.info(f"  - Exclude: {self.enable_exclude_filter}")
        self.logger.info(f"  - Confidence threshold: {self.confidence_threshold * 100:.0f}%")
    
    def _init_driver(self) -> webdriver.Chrome:
        """Initialize Selenium Chrome driver"""
        try:
            chrome_options = Options()
            chrome_options.add_argument("--headless")
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument(
                "user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36"
            )
            driver = webdriver.Chrome(options=chrome_options)
            self.logger.info("Chrome driver initialized")
            return driver
        except Exception as e:
            self.logger.error(f"Failed to initialize Chrome driver: {e}")
            raise
    
    def _load_page(self) -> bool:
        """Load KHCU schedule page"""
        try:
            if not self.driver:
                self.driver = self._init_driver()
            
            self.logger.info(f"Loading {self.schedule_url}")
            self.driver.get(self.schedule_url)
            
            try:
                WebDriverWait(self.driver, 10).until(
                    EC.presence_of_all_elements_located((By.CLASS_NAME, "scheduleList"))
                )
            except:
                import time
                time.sleep(3)
            
            import time
            time.sleep(2)
            
            self.logger.info("Page loaded successfully")
            return True
        except Exception as e:
            self.logger.error(f"Error loading page: {e}")
            return False
    
    def _calculate_confidence(self, text: str, keywords: List[str]) -> Tuple[float, int]:
        """
        Calculate confidence score for keyword matching
        
        Returns: (confidence_score, match_count)
        """
        text_lower = text.lower()
        matches = sum(1 for keyword in keywords if keyword in text_lower)
        confidence = matches / len(keywords) if keywords else 0
        
        return confidence, matches
    
    def _check_department_match(self, text: str) -> Tuple[Optional[str], float]:
        """
        Check if text matches any department
        
        Returns: (department_name, confidence_score)
        """
        text_lower = text.lower()
        
        for dept_name, dept_config in FilterConfig.DEPARTMENTS.items():
            all_keywords = dept_config['korean'] + dept_config['english']
            confidence, matches = self._calculate_confidence(text_lower, all_keywords)
            
            if confidence >= self.confidence_threshold:
                self.logger.debug(
                    f"Department match '{dept_name}': {matches}/{len(all_keywords)} keywords ({confidence*100:.0f}%)"
                )
                return dept_name, confidence
        
        return None, 0.0
    
    def _check_item_type(self, text: str) -> Tuple[Optional[str], float]:
        """
        Check what type of item this is
        
        Returns: (item_type, priority)
        """
        text_lower = text.lower()
        
        for item_type, item_config in FilterConfig.ITEM_TYPES.items():
            all_keywords = item_config['korean'] + item_config['english']
            confidence, matches = self._calculate_confidence(text_lower, all_keywords)
            
            if confidence >= self.confidence_threshold:
                self.logger.debug(
                    f"Item type match '{item_type}': {matches}/{len(all_keywords)} keywords ({confidence*100:.0f}%)"
                )
                return item_type, item_config['priority']
        
        return None, 999  # High number = low priority
    
    def _check_exclude_patterns(self, text: str) -> bool:
        """
        Check if item should be excluded
        
        Returns: True if should be excluded, False otherwise
        """
        text_lower = text.lower()
        
        for exclude_type, exclude_config in FilterConfig.EXCLUDE.items():
            all_keywords = exclude_config['korean'] + exclude_config['english']
            confidence, matches = self._calculate_confidence(text_lower, all_keywords)
            
            if confidence >= self.confidence_threshold:
                self.logger.debug(
                    f"Exclude match '{exclude_type}': {matches}/{len(all_keywords)} keywords"
                )
                return True
        
        return False
    
    def _clean_title(self, title: str) -> str:
        """Clean title of stray characters"""
        if not title:
            return title
        cleaned = re.sub(r'[a-zA-Z]+\s*$', '', title).strip()
        cleaned = re.sub(r'[/\\]+\s*$', '', cleaned).strip()
        return cleaned
    
    def _is_in_date_range(self, article_date: Optional[str]) -> bool:
        """Check if date is within configured range"""
        if not article_date:
            return False
        
        try:
            article_dt = datetime.strptime(article_date, '%Y-%m-%d')
            today = datetime.now()
            future_cutoff = today + timedelta(days=self.date_filter_days)
            return today.date() <= article_dt.date() <= future_cutoff.date()
        except Exception as e:
            self.logger.debug(f"Date check error: {e}")
            return False
    
    def fetch_articles(self) -> List[Dict[str, Any]]:
        """Fetch raw articles from page"""
        articles = []
        
        try:
            if not self._load_page():
                return articles
            
            schedule_items = self.driver.find_elements(By.CSS_SELECTOR, ".scheduleList > li")
            self.logger.info(f"Found {len(schedule_items)} total items on page")
            
            for item in schedule_items:
                try:
                    date_elem = item.find_element(By.CLASS_NAME, "date")
                    date_text = date_elem.text.strip()
                    
                    spans = item.find_elements(By.TAG_NAME, "span")
                    title = ""
                    if len(spans) > 1:
                        title = spans[1].text.strip()
                        title = self._clean_title(title)
                    
                    if not title:
                        continue
                    
                    article = {
                        'title': title,
                        'url': self.schedule_url,
                        'content': f"{date_text}: {title}",
                        'date_text': date_text,
                        'source': self.source_name,
                        'published_date': self._parse_date(date_text),
                    }
                    
                    articles.append(article)
                except Exception as e:
                    self.logger.debug(f"Extraction error: {e}")
            
            self.logger.info(f"Extracted {len(articles)} raw articles")
            return articles
            
        except Exception as e:
            self.logger.error(f"Error fetching articles: {e}")
            return articles
    
    def _parse_date(self, date_text: str) -> Optional[str]:
        """Parse Korean date format to YYYY-MM-DD"""
        try:
            match = re.match(r'(\d{2})\.(\d{2})', date_text)
            if not match:
                return None
            
            month, day = int(match.group(1)), int(match.group(2))
            year = datetime.now().year
            date_obj = datetime(year, month, day)
            return date_obj.strftime('%Y-%m-%d')
        except Exception as e:
            self.logger.debug(f"Date parse error: {e}")
            return None
    
    def parse_article(self, raw_data: Dict[str, Any]) -> Optional[Article]:
        """Parse article with advanced filtering"""
        text = f"{raw_data.get('title', '')} {raw_data.get('content', '')}"
        
        # Check exclusions first
        if self.enable_exclude_filter and self._check_exclude_patterns(text):
            self.logger.debug(f"Excluded (pattern match): {raw_data.get('title', '')[:50]}")
            return None
        
        # Check date range
        if not self._is_in_date_range(raw_data.get('published_date')):
            self.logger.debug(f"Filtered (date range): {raw_data.get('title', '')[:50]}")
            return None
        
        # Check department match (optional)
        department, dept_confidence = self._check_department_match(text)
        
        # Check item type (optional)
        item_type, item_priority = self._check_item_type(text)
        
        # Decide if we should include this article
        include = True
        
        if self.enable_department_filter and self.enable_item_type_filter:
            # Strict: require BOTH department AND item type
            include = (department is not None) and (item_type is not None)
            reason = "strict (dept + type)"
        elif self.enable_department_filter:
            # Only department filter
            include = (department is not None)
            reason = "dept only"
        elif self.enable_item_type_filter:
            # Only item type filter
            include = (item_type is not None)
            reason = "type only"
        else:
            # No filters - include all (except excluded/past)
            reason = "no filters"
        
        if not include:
            self.logger.debug(f"Filtered ({reason}): {raw_data.get('title', '')[:50]}")
            return None
        
        # Create article
        try:
            article = Article(
                title=raw_data.get('title', ''),
                url=raw_data.get('url', ''),
                content=raw_data.get('content', ''),
                source=self.source_name,
                published_date=raw_data.get('published_date'),
                department=department,
                metadata={
                    'fetched_at': datetime.now().isoformat(),
                    'source_name': self.source_name,
                    'date_text': raw_data.get('date_text'),
                    'item_type': item_type,
                    'item_priority': item_priority,
                    'department_confidence': dept_confidence,
                }
            )
            
            self.logger.debug(f"Included: {article.title} (dept={department}, type={item_type})")
            return article
            
        except Exception as e:
            self.logger.error(f"Parse error: {e}")
            return None
    
    def get_source_name(self) -> str:
        """Return source identifier"""
        return self.source_name
    
    def scrape(self) -> List[Article]:
        """Main scraping with advanced filtering"""
        try:
            raw_articles = self.fetch_articles()
            articles = []
            
            excluded_count = 0
            filtered_count = 0
            
            for raw in raw_articles:
                article = self.parse_article(raw)
                
                if article is None:
                    # Count why it was filtered
                    if self._check_exclude_patterns(f"{raw.get('title', '')} {raw.get('content', '')}"):
                        excluded_count += 1
                    else:
                        filtered_count += 1
                else:
                    articles.append(article)
            
            self.logger.info(
                f"Scraped {len(articles)} articles "
                f"(filtered: {filtered_count}, excluded: {excluded_count}) "
                f"from {self.source_name}"
            )
            
            return articles
            
        except Exception as e:
            self.logger.error(f"Scraping failed: {e}")
            return []
        
        finally:
            if self.driver:
                try:
                    self.driver.quit()
                    self.driver = None
                except Exception as e:
                    self.logger.error(f"Driver error: {e}")
    
    def __del__(self):
        """Cleanup"""
        if self.driver:
            try:
                self.driver.quit()
            except:
                pass


# Test
if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    print("🧪 Testing KHCU Scraper with Advanced Filtering")
    print("=" * 60)
    
    # Test with different filter strategies
    strategies = [
        {
            'name': 'Strategy 1: Department Only',
            'enable_department_filter': True,
            'enable_item_type_filter': False,
            'enable_exclude_filter': True,
        },
        {
            'name': 'Strategy 2: Strict (Dept + Type)',
            'enable_department_filter': True,
            'enable_item_type_filter': True,
            'enable_exclude_filter': True,
        },
        {
            'name': 'Strategy 3: No Filters',
            'enable_department_filter': False,
            'enable_item_type_filter': False,
            'enable_exclude_filter': True,  # Still exclude holidays/expired
        },
    ]
    
    for strategy in strategies:
        print(f"\n{strategy['name']}")
        print("-" * 60)
        
        config = {
            'date_filter_days': 120,
            'confidence_threshold': 0.10,
            **{k: v for k, v in strategy.items() if k != 'name'}
        }
        
        scraper = KhcuScraperAdvanced(config)
        articles = scraper.scrape()
        
        print(f"✅ Found {len(articles)} relevant articles")
        for i, article in enumerate(articles[:5], 1):
            print(f"\n{i}. {article.title}")
            print(f"   Type: {article.metadata.get('item_type', 'N/A')}")
            print(f"   Dept: {article.metadata.get('department', 'N/A')}")
    
    print("\n" + "=" * 60)
    print("✅ Advanced filtering test complete")
