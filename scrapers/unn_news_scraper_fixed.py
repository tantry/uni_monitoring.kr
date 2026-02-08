"""
UNN News RSS Scraper - Fixed imports version
"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from core.base_scraper import BaseScraper
    from models.article import Article
    HAS_DEPS = True
except ImportError:
    # Fallback for testing
    class BaseScraper:
        def __init__(self, config):
            self.config = config
            self.base_url = config.get('url', '')
            import requests
            self.session = requests.Session()
    
    class Article:
        def __init__(self, **kwargs):
            self.__dict__.update(kwargs)
    HAS_DEPS = False

import time
import re
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
import feedparser

logger = logging.getLogger(__name__)

# Rest of the UNNNewsScraper class (same as before)...
# [You would copy the full UNNNewsScraper class here]
