#!/usr/bin/env python3
"""
Factory for creating and managing university admission scraper instances
"""
import importlib
import inspect
from typing import Dict, List, Type, Optional, Any
from pathlib import Path
import yaml
import logging

from core.base_scraper import BaseScraper

class ScraperFactory:
    """
    Factory for creating scraper instances with dynamic loading
    
    Features:
    - Dynamic scraper discovery and loading
    - Configuration-driven instantiation
    - Singleton pattern for scraper instances
    - Health monitoring and error recovery
    """
    
    def __init__(self, config_dir: str = "config", scrapers_dir: str = "scrapers"):
        """
        Initialize scraper factory
        
        Args:
            config_dir: Directory containing configuration files
            scrapers_dir: Directory containing scraper implementations
        """
        self.config_dir = Path(config_dir)
        self.scrapers_dir = Path(scrapers_dir)
        
        # Setup logging
        self.logger = logging.getLogger("scraper_factory")
        self._setup_logger()
        
        # Load configuration
        self.sources_config = self._load_config('sources.yaml')
        
        # Cache for instantiated scrapers
        self._scraper_cache: Dict[str, BaseScraper] = {}
        
        # Health tracking
        self.scraper_health: Dict[str, Dict[str, Any]] = {}
        
        self.logger.info(f"Initialized ScraperFactory with config: {self.config_dir}")
    
    def _setup_logger(self):
        """Setup logger for the factory"""
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
            self.logger.setLevel(logging.INFO)
    
    def _load_config(self, filename: str) -> Dict[str, Any]:
        """
        Load configuration from YAML file
        
        Args:
            filename: Configuration file name
            
        Returns:
            Configuration dictionary
            
        Raises:
            FileNotFoundError: If configuration file doesn't exist
            yaml.YAMLError: If configuration file has syntax errors
        """
        config_path = self.config_dir / filename
        
        if not config_path.exists():
            error_msg = f"Configuration file not found: {config_path}"
            self.logger.error(error_msg)
            raise FileNotFoundError(error_msg)
        
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
            
            if not config:
                self.logger.warning(f"Configuration file is empty: {config_path}")
                return {}
            
            self.logger.info(f"Loaded configuration from {config_path}")
            return config
            
        except yaml.YAMLError as e:
            error_msg = f"YAML syntax error in {config_path}: {e}"
            self.logger.error(error_msg)
            raise
        except Exception as e:
            error_msg = f"Failed to load configuration from {config_path}: {e}"
            self.logger.error(error_msg)
            raise
    
    def get_available_sources(self) -> List[str]:
        """
        Get list of all available source IDs from configuration
        
        Returns:
            List of source identifiers
        """
        sources = self.sources_config.get('sources', {})
        return list(sources.keys())
    
    def get_enabled_sources(self) -> List[str]:
        """
        Get list of enabled source IDs
        
        Returns:
            List of enabled source identifiers
        """
        sources = self.sources_config.get('sources', {})
        return [
            source_id for source_id, config in sources.items()
            if config.get('enabled', False)
        ]
    
    def list_available_scrapers(self) -> List[str]:
        """
        List all available scraper source IDs.
        
        Returns:
            List of source identifiers
        """
        return self.get_available_sources()

    def get_source_config(self, source_id: str) -> Optional[Dict[str, Any]]:
        """
        Get configuration for a specific source
        
        Args:
            source_id: Source identifier
            
        Returns:
            Source configuration dictionary or None if not found
        """
        sources = self.sources_config.get('sources', {})
        return sources.get(source_id)
    
    def _validate_scraper_class(self, scraper_class: Type) -> bool:
        """
        Validate that a class is a proper scraper implementation
        
        Args:
            scraper_class: Class to validate
            
        Returns:
            True if valid scraper, False otherwise
        """
        # Check if it's a class
        if not inspect.isclass(scraper_class):
            self.logger.warning(f"Not a class: {scraper_class}")
            return False
        
        # Check if it inherits from BaseScraper
        if not issubclass(scraper_class, BaseScraper):
            self.logger.warning(f"Class {scraper_class.__name__} does not inherit from BaseScraper")
            return False
        
        # Check for required abstract methods
        required_methods = ['fetch_articles', 'parse_article']
        for method in required_methods:
            if not hasattr(scraper_class, method):
                self.logger.warning(f"Class {scraper_class.__name__} missing required method: {method}")
                return False
        
        # Check if methods are implemented (not abstract)
        for method in required_methods:
            method_obj = getattr(scraper_class, method)
            if getattr(method_obj, '__isabstractmethod__', False):
                self.logger.warning(f"Class {scraper_class.__name__} has abstract method: {method}")
                return False
        
        return True
    
    def _import_scraper_module(self, module_name: str) -> Optional[Any]:
        """
        Import scraper module dynamically
        
        Args:
            module_name: Module name to import
            
        Returns:
            Imported module or None if import fails
        """
        try:
            module = importlib.import_module(module_name)
            self.logger.debug(f"Successfully imported module: {module_name}")
            return module
        except ImportError as e:
            self.logger.error(f"Failed to import module {module_name}: {e}")
            return None
        except Exception as e:
            self.logger.error(f"Unexpected error importing module {module_name}: {e}")
            return None
    
    def _discover_scraper_class(self, module: Any, class_name: str) -> Optional[Type[BaseScraper]]:
        """
        Discover scraper class in module
        
        Args:
            module: Imported module
            class_name: Expected class name
            
        Returns:
            Scraper class or None if not found
        """
        try:
            # Try to get the class by name
            scraper_class = getattr(module, class_name)
            
            # Validate it's a proper scraper class
            if self._validate_scraper_class(scraper_class):
                self.logger.debug(f"Found valid scraper class: {class_name}")
                return scraper_class
            else:
                self.logger.warning(f"Class {class_name} failed validation")
                return None
                
        except AttributeError:
            # Class not found by name, search for any BaseScraper subclass
            self.logger.debug(f"Class {class_name} not found, searching for scraper classes...")
            
            for name, obj in inspect.getmembers(module):
                if inspect.isclass(obj) and issubclass(obj, BaseScraper) and obj != BaseScraper:
                    if self._validate_scraper_class(obj):
                        self.logger.info(f"Found scraper class {name} (expected {class_name})")
                        return obj
            
            self.logger.warning(f"No valid scraper class found in module")
            return None
    
    def create_scraper(self, source_id: str, force_reload: bool = False) -> Optional[BaseScraper]:
        """
        Create scraper instance for given source
        
        Args:
            source_id: Source identifier
            force_reload: Force recreation even if cached
            
        Returns:
            Scraper instance or None if creation fails
        """
        # Check cache first (unless force reload)
        if not force_reload and source_id in self._scraper_cache:
            self.logger.debug(f"Returning cached scraper for {source_id}")
            return self._scraper_cache[source_id]
        
        # Get source configuration
        source_config = self.get_source_config(source_id)
        if not source_config:
            self.logger.error(f"Source configuration not found: {source_id}")
            return None
        
        # Check if source is enabled
        if not source_config.get('enabled', False):
            self.logger.warning(f"Source {source_id} is disabled in configuration")
            return None
        
        # Get scraper class name from config
        scraper_class_name = source_config.get('scraper_class')
        if not scraper_class_name:
            self.logger.error(f"No scraper_class specified for {source_id}")
            return None
        
        # Construct module name
        module_name = f"scrapers.{scraper_class_name.lower()}"
        
        # Import module
        module = self._import_scraper_module(module_name)
        if not module:
            # Try alternative naming (without .py extension issues)
            module_name_alt = f"scrapers.{scraper_class_name}"
            module = self._import_scraper_module(module_name_alt)
            if not module:
                self.logger.error(f"Failed to import scraper module for {source_id}")
                return None
        
        # Discover scraper class
        scraper_class = self._discover_scraper_class(module, scraper_class_name)
        if not scraper_class:
            self.logger.error(f"Failed to find valid scraper class for {source_id}")
            return None
        
        try:
            # Instantiate scraper with configuration
            scraper_instance = scraper_class(source_config)
            
            # Update health tracking
            self.scraper_health[source_id] = {
                'last_created': self._get_current_timestamp(),
                'creation_success': True,
                'error_count': 0,
                'instance': scraper_instance.__class__.__name__
            }
            
            # Cache the instance
            self._scraper_cache[source_id] = scraper_instance
            
            self.logger.info(f"Created scraper instance for {source_id}: {scraper_instance.__class__.__name__}")
            return scraper_instance
            
        except Exception as e:
            self.logger.error(f"Failed to instantiate scraper for {source_id}: {e}")
            
            # Update health tracking with error
            self.scraper_health[source_id] = {
                'last_attempt': self._get_current_timestamp(),
                'creation_success': False,
                'error_count': self.scraper_health.get(source_id, {}).get('error_count', 0) + 1,
                'last_error': str(e)
            }
            
            return None
    
    def create_all_enabled(self, force_reload: bool = False) -> List[BaseScraper]:
        """
        Create all enabled scrapers
        
        Args:
            force_reload: Force recreation of all scrapers
            
        Returns:
            List of created scraper instances
        """
        enabled_sources = self.get_enabled_sources()
        self.logger.info(f"Creating {len(enabled_sources)} enabled scrapers")
        
        scrapers = []
        for source_id in enabled_sources:
            scraper = self.create_scraper(source_id, force_reload)
            if scraper:
                scrapers.append(scraper)
            else:
                self.logger.warning(f"Failed to create scraper for {source_id}")
        
        self.logger.info(f"Successfully created {len(scrapers)}/{len(enabled_sources)} scrapers")
        return scrapers
    
    def get_scraper(self, source_id: str) -> Optional[BaseScraper]:
        """
        Get scraper instance (create if not exists)
        
        Args:
            source_id: Source identifier
            
        Returns:
            Scraper instance or None
        """
        return self.create_scraper(source_id, force_reload=False)
    
    def reload_configuration(self):
        """Reload configuration from files"""
        self.logger.info("Reloading scraper factory configuration")
        
        try:
            old_config = self.sources_config
            self.sources_config = self._load_config('sources.yaml')
            
            # Clear cache if configuration changed significantly
            if old_config != self.sources_config:
                self.logger.info("Configuration changed, clearing scraper cache")
                self._scraper_cache.clear()
            
        except Exception as e:
            self.logger.error(f"Failed to reload configuration: {e}")
    
    def get_scraper_health(self, source_id: str) -> Dict[str, Any]:
        """
        Get health information for a scraper
        
        Args:
            source_id: Source identifier
            
        Returns:
            Health information dictionary
        """
        health = self.scraper_health.get(source_id, {})
        
        # Add basic info if not in health tracking yet
        if not health:
            config = self.get_source_config(source_id)
            if config:
                health = {
                    'source_id': source_id,
                    'enabled': config.get('enabled', False),
                    'configured': True,
                    'instantiated': source_id in self._scraper_cache
                }
            else:
                health = {
                    'source_id': source_id,
                    'configured': False,
                    'error': 'Source not configured'
                }
        
        return health
    
    def get_all_health(self) -> Dict[str, Dict[str, Any]]:
        """
        Get health information for all scrapers
        
        Returns:
            Dictionary of health information for all sources
        """
        all_health = {}
        
        for source_id in self.get_available_sources():
            all_health[source_id] = self.get_scraper_health(source_id)
        
        return all_health
    
    def _get_current_timestamp(self) -> str:
        """Get current timestamp string"""
        from datetime import datetime
        return datetime.now().isoformat()
    
    def register_custom_scraper(self, source_id: str, scraper_class: Type[BaseScraper], 
                               config: Optional[Dict[str, Any]] = None) -> bool:
        """
        Register a custom scraper class at runtime
        
        Args:
            source_id: Source identifier
            scraper_class: Scraper class to register
            config: Configuration for the scraper
            
        Returns:
            True if registration successful, False otherwise
        """
        if not self._validate_scraper_class(scraper_class):
            self.logger.error(f"Invalid scraper class for registration: {scraper_class}")
            return False
        
        # Use provided config or create default
        if not config:
            config = {
                'name': source_id.replace('_', ' ').title(),
                'enabled': True,
                'scraper_class': scraper_class.__name__
            }
        
        # Add to configuration
        if 'sources' not in self.sources_config:
            self.sources_config['sources'] = {}
        
        self.sources_config['sources'][source_id] = config
        
        # Clear cache for this source
        if source_id in self._scraper_cache:
            del self._scraper_cache[source_id]
        
        self.logger.info(f"Registered custom scraper: {source_id} -> {scraper_class.__name__}")
        return True
    
    def cleanup(self):
        """Cleanup resources and clear cache"""
        self.logger.info("Cleaning up scraper factory")
        
        # Call cleanup on all cached scrapers if they have cleanup method
        for source_id, scraper in self._scraper_cache.items():
            if hasattr(scraper, 'cleanup') and callable(scraper.cleanup):
                try:
                    scraper.cleanup()
                except Exception as e:
                    self.logger.warning(f"Error cleaning up scraper {source_id}: {e}")
        
        # Clear cache
        self._scraper_cache.clear()
        self.logger.info("Cleared scraper cache")
