#!/usr/bin/env python3
"""
Dynamic department filtering system for university admission announcements
"""
import yaml
import re
from typing import List, Optional, Dict, Any, Set
from pathlib import Path
from datetime import datetime
import logging
from enum import Enum

from models.article import Article, Department

class MatchStrategy(Enum):
    """Strategy for matching articles to departments"""
    EXACT = "exact"
    CONTAINS = "contains"
    REGEX = "regex"
    FUZZY = "fuzzy"

class FilterEngine:
    """
    Dynamic department filtering system with configurable rules
    
    Features:
    - YAML-based configuration
    - Hot-reloading of filter rules
    - Multiple matching strategies
    - Department priority system
    - Custom keyword weighting
    """
    
    def __init__(self, config_path: str = "config/filters.yaml"):
        """
        Initialize filter engine with configuration
        
        Args:
            config_path: Path to filters configuration YAML file
        """
        self.config_path = Path(config_path)
        self.logger = logging.getLogger("filter_engine")
        self._setup_logger()
        
        # Load initial configuration
        self.departments = self._load_departments()
        self.match_strategy = MatchStrategy.CONTAINS
        self.min_confidence = 0.7
        self.enable_fallback = True
        
        self.logger.info(f"Initialized FilterEngine with {len(self.departments)} departments")
    
    def _setup_logger(self):
        """Setup logger for the filter engine"""
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
            self.logger.setLevel(logging.INFO)
    
    def _load_departments(self) -> Dict[str, Dict[str, Any]]:
        """
        Load department configuration from YAML file
        
        Returns:
            Dictionary of department configurations
        """
        if not self.config_path.exists():
            self.logger.warning(f"Config file not found: {self.config_path}")
            return self._create_default_config()
        
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
            
            departments = config.get('departments', {})
            
            # Validate department configurations
            validated_departments = {}
            for dept_id, dept_config in departments.items():
                validated = self._validate_department_config(dept_id, dept_config)
                if validated:
                    validated_departments[dept_id] = validated
            
            self.logger.info(f"Loaded {len(validated_departments)} departments from {self.config_path}")
            return validated_departments
            
        except yaml.YAMLError as e:
            self.logger.error(f"YAML parsing error in {self.config_path}: {e}")
            return self._create_default_config()
        except Exception as e:
            self.logger.error(f"Failed to load filters: {e}")
            return self._create_default_config()
    
    def _validate_department_config(self, dept_id: str, config: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Validate department configuration
        
        Args:
            dept_id: Department identifier
            config: Department configuration dictionary
            
        Returns:
            Validated configuration or None if invalid
        """
        required_fields = ['name', 'keywords']
        
        for field in required_fields:
            if field not in config:
                self.logger.warning(f"Department '{dept_id}' missing required field: {field}")
                return None
        
        # Ensure keywords is a list
        if not isinstance(config['keywords'], list):
            self.logger.warning(f"Department '{dept_id}' keywords must be a list")
            return None
        
        # Set defaults for optional fields
        config.setdefault('emoji', '🎓')
        config.setdefault('priority', 99)
        config.setdefault('enabled', True)
        config.setdefault('description', '')
        config.setdefault('weight', 1.0)
        
        return config
    
    def _create_default_config(self) -> Dict[str, Dict[str, Any]]:
        """
        Create default department configuration
        
        Returns:
            Default department configuration
        """
        self.logger.info("Creating default department configuration")
        
        default_departments = {
            'music': {
                'name': '음악학과',
                'keywords': ['음악', 'music', '실용음악', '성악', '작곡', '교향곡', '오케스트라'],
                'emoji': '🎵',
                'priority': 1,
                'enabled': True,
                'description': '음악 관련 학과',
                'weight': 1.0
            },
            'korean': {
                'name': '국어국문학과',
                'keywords': ['한국어', '국어', '국어국문', '국문학', '한국언어', '한글'],
                'emoji': '📚',
                'priority': 2,
                'enabled': True,
                'description': '국어국문학 관련 학과',
                'weight': 1.0
            },
            'english': {
                'name': '영어영문학과',
                'keywords': ['영어', '영어영문', '영문학', '영미언어', '영미문화'],
                'emoji': '🔤',
                'priority': 3,
                'enabled': True,
                'description': '영어영문학 관련 학과',
                'weight': 1.0
            },
            'liberal': {
                'name': '인문학부',
                'keywords': ['인문', '인문학', '교양', '교양교육', '자유전공', '기초교육'],
                'emoji': '📖',
                'priority': 4,
                'enabled': True,
                'description': '인문학 관련 학과',
                'weight': 1.0
            }
        }
        
        # Save default configuration
        self._save_config({'departments': default_departments})
        
        return default_departments
    
    def _save_config(self, config: Dict[str, Any]):
        """
        Save configuration to YAML file
        
        Args:
            config: Configuration dictionary
        """
        try:
            self.config_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.config_path, 'w', encoding='utf-8') as f:
                yaml.dump(config, f, allow_unicode=True, sort_keys=False)
            self.logger.info(f"Saved configuration to {self.config_path}")
        except Exception as e:
            self.logger.error(f"Failed to save configuration: {e}")
    
    def detect_department(self, article_text: str, title: Optional[str] = None) -> Optional[str]:
        """
        Detect which department an article belongs to
        
        Args:
            article_text: Article content text
            title: Article title (optional, for additional matching)
            
        Returns:
            Department identifier or None if no match
        """
        if not article_text:
            return None
        
        # Combine title and content for matching
        search_text = article_text.lower()
        if title:
            search_text = f"{title.lower()} {search_text}"
        
        # Track matches with confidence scores
        matches = {}
        
        for dept_id, dept_config in self.departments.items():
            if not dept_config.get('enabled', True):
                continue
            
            confidence = self._calculate_match_confidence(
                search_text, 
                dept_config['keywords'],
                dept_config.get('weight', 1.0)
            )
            
            if confidence >= self.min_confidence:
                matches[dept_id] = {
                    'confidence': confidence,
                    'priority': dept_config.get('priority', 99)
                }
        
        if not matches:
            return None
        
        # Select best match (highest confidence, then highest priority)
        best_match = max(
            matches.items(),
            key=lambda x: (x[1]['confidence'], -x[1]['priority'])
        )[0]
        
        self.logger.debug(f"Matched '{best_match}' with confidence {matches[best_match]['confidence']}")
        return best_match
    
    def _calculate_match_confidence(self, text: str, keywords: List[str], weight: float = 1.0) -> float:
        """
        Calculate match confidence score
        
        Args:
            text: Text to search in
            keywords: List of keywords to match
            weight: Department weight multiplier
            
        Returns:
            Confidence score between 0.0 and 1.0
        """
        if not keywords:
            return 0.0
        
        matches = 0
        total_keywords = len(keywords)
        
        for keyword in keywords:
            keyword_lower = keyword.lower()
            
            if self.match_strategy == MatchStrategy.EXACT:
                # Exact word match (with word boundaries)
                pattern = r'\b' + re.escape(keyword_lower) + r'\b'
                if re.search(pattern, text):
                    matches += 1
            elif self.match_strategy == MatchStrategy.REGEX:
                # Regex match
                try:
                    if re.search(keyword_lower, text):
                        matches += 1
                except re.error:
                    # Fallback to contains if regex is invalid
                    if keyword_lower in text:
                        matches += 1
            else:  # CONTAINS (default)
                # Simple substring match
                if keyword_lower in text:
                    matches += 1
        
        # Calculate base confidence
        base_confidence = matches / total_keywords if total_keywords > 0 else 0.0
        
        # Apply weight and normalize
        confidence = min(base_confidence * weight, 1.0)
        
        return confidence
    
    def add_department(self, dept_id: str, name: str, keywords: List[str], 
                      emoji: str = "🎓", priority: int = 99, enabled: bool = True) -> bool:
        """
        Add new department at runtime
        
        Args:
            dept_id: Department identifier
            name: Display name
            keywords: List of keywords for matching
            emoji: Emoji for the department
            priority: Match priority (lower = higher priority)
            enabled: Whether department is enabled
            
        Returns:
            True if successful, False otherwise
        """
        if dept_id in self.departments:
            self.logger.warning(f"Department '{dept_id}' already exists")
            return False
        
        new_department = {
            'name': name,
            'keywords': keywords,
            'emoji': emoji,
            'priority': priority,
            'enabled': enabled,
            'description': f"Added {datetime.now().strftime('%Y-%m-%d')}",
            'weight': 1.0
        }
        
        self.departments[dept_id] = new_department
        
        # Save updated configuration
        self._save_config({'departments': self.departments})
        
        self.logger.info(f"Added new department: {name} ({dept_id})")
        return True
    
    def update_department(self, dept_id: str, **kwargs) -> bool:
        """
        Update existing department configuration
        
        Args:
            dept_id: Department identifier
            **kwargs: Fields to update
            
        Returns:
            True if successful, False otherwise
        """
        if dept_id not in self.departments:
            self.logger.warning(f"Department '{dept_id}' not found")
            return False
        
        # Update specified fields
        for key, value in kwargs.items():
            if key in self.departments[dept_id]:
                self.departments[dept_id][key] = value
        
        # Save updated configuration
        self._save_config({'departments': self.departments})
        
        self.logger.info(f"Updated department: {dept_id}")
        return True
    
    def get_department_info(self, dept_id: str) -> Optional[Dict[str, Any]]:
        """
        Get department configuration
        
        Args:
            dept_id: Department identifier
            
        Returns:
            Department configuration or None if not found
        """
        return self.departments.get(dept_id)
    
    def get_all_departments(self, enabled_only: bool = False) -> Dict[str, Dict[str, Any]]:
        """
        Get all department configurations
        
        Args:
            enabled_only: Whether to return only enabled departments
            
        Returns:
            Dictionary of department configurations
        """
        if enabled_only:
            return {dept_id: config for dept_id, config in self.departments.items() 
                    if config.get('enabled', True)}
        return self.departments
    
    def filter_article(self, article: Article) -> Optional[str]:
        """
        Filter article and assign department
        
        Args:
            article: Article to filter
            
        Returns:
            Assigned department identifier or None
        """
        # Combine title and content for filtering
        search_text = article.content.lower()
        if article.title:
            search_text = f"{article.title.lower()} {search_text}"
        
        dept_id = self.detect_department(search_text, article.title)
        
        if dept_id:
            # Convert string department to Department enum
            try:
                article.department = Department(dept_id)
                self.logger.debug(f"Assigned department '{dept_id}' to article: {article.title[:50]}...")
                return dept_id
            except ValueError:
                self.logger.warning(f"Unknown department: {dept_id}")
        
        # Fallback to general if enabled
        if self.enable_fallback:
            article.department = Department.GENERAL
            return 'general'
        
        return None
    
    def reload_config(self):
        """Reload configuration from file"""
        self.logger.info("Reloading filter configuration")
        self.departments = self._load_departments()
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Get filter engine statistics
        
        Returns:
            Dictionary of statistics
        """
        enabled_count = sum(1 for config in self.departments.values() 
                           if config.get('enabled', True))
        
        total_keywords = sum(len(config.get('keywords', [])) 
                            for config in self.departments.values())
        
        return {
            'total_departments': len(self.departments),
            'enabled_departments': enabled_count,
            'total_keywords': total_keywords,
            'avg_keywords_per_dept': total_keywords / len(self.departments) if self.departments else 0,
            'match_strategy': self.match_strategy.value,
            'min_confidence': self.min_confidence,
            'config_path': str(self.config_path),
            'last_loaded': datetime.now().isoformat()
        }
