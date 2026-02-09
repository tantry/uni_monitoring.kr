from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, Dict, Any
from enum import Enum
import hashlib

class Department(Enum):
    """Department categories for filtering"""
    MUSIC = "music"
    KOREAN = "korean"
    ENGLISH = "english"
    LIBERAL = "liberal"
    UNKNOWN = "unknown"

@dataclass
class Article:
    """Unified article data model"""
    title: str
    url: str
    content: str
    source: str
    published_date: Optional[str] = None
    department: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        if not self.published_date:
            self.published_date = datetime.now().isoformat()

    def get_hash(self) -> str:
        """Generate unique hash for duplicate detection"""
        content = f"{self.title}:{self.url}"
        return hashlib.md5(content.encode()).hexdigest()

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization"""
        return {
            'title': self.title,
            'url': self.url,
            'content': self.content,
            'source': self.source,
            'published_date': self.published_date,
            'department': self.department,
            'metadata': self.metadata,
            'hash': self.get_hash()
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'Article':
        """Create Article from dictionary"""
        return cls(
            title=data.get('title', ''),
            url=data.get('url', ''),
            content=data.get('content', ''),
            source=data.get('source', ''),
            published_date=data.get('published_date'),
            department=data.get('department'),
            metadata=data.get('metadata', {})
        )
