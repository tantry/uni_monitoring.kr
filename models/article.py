from dataclasses import dataclass
from datetime import datetime
from typing import Optional

@dataclass
class Article:
    title: str
    url: str
    content: str
    source: str
    published_date: Optional[str] = None
    department: Optional[str] = None
    
    def __post_init__(self):
        if not self.published_date:
            self.published_date = datetime.now().isoformat()
    
    def get_hash(self) -> str:
        """Generate unique hash for duplicate detection"""
        import hashlib
        content = f"{self.title}:{self.url}"
        return hashlib.md5(content.encode()).hexdigest()
