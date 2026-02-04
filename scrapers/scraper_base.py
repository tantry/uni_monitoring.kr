"""
Base class for all university admission scrapers
Standardizes output format and file handling
"""
from abc import ABC, abstractmethod
from datetime import datetime
import json
import os

class BaseScraper(ABC):
    """Base class that all scrapers should inherit from"""
    
    def __init__(self, source_name, source_config):
        self.source_name = source_name
        self.source_config = source_config
        self.data_dir = "uni_monitor_data"
        self.detected_file = os.path.join(
            self.data_dir, 
            f"detected_{source_name}.json"
        )
        
        # Ensure data directory exists
        os.makedirs(self.data_dir, exist_ok=True)
    
    @abstractmethod
    def scrape(self):
        """Main scraping method to be implemented by each scraper"""
        pass
    
    @abstractmethod
    def normalize_program_data(self, raw_data):
        """Convert scraped data to standardized format"""
        pass
    
    def save_detected(self, programs):
        """Save detected programs to JSON file"""
        with open(self.detected_file, 'w', encoding='utf-8') as f:
            json.dump({
                'last_updated': datetime.now().isoformat(),
                'source': self.source_name,
                'programs': programs
            }, f, ensure_ascii=False, indent=2)
    
    def load_previous(self):
        """Load previously detected programs"""
        if os.path.exists(self.detected_file):
            with open(self.detected_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {'programs': []}
    
    def find_new_programs(self, current_programs):
        """Compare with previous runs to find new programs"""
        previous = self.load_previous()
        previous_ids = {p['id'] for p in previous.get('programs', []) 
                       if 'id' in p}
        
        new_programs = []
        for program in current_programs:
            if 'id' not in program:
                # Generate a simple ID if not provided
                program['id'] = f"{self.source_name}_{hash(frozenset(program.items()))}"
            
            if program['id'] not in previous_ids:
                new_programs.append(program)
        
        return new_programs
