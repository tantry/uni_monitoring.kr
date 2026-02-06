#!/usr/bin/env python3
"""
Article data model for university admission announcements
"""
from dataclasses import dataclass, asdict, field
from datetime import datetime
from typing import Optional, Dict, Any, List
from enum import Enum
import json

class ArticleStatus(Enum):
    """Status of an article in the processing pipeline"""
    NEW = "new"
    PROCESSED = "processed" 
    FILTERED = "filtered"
    SENT = "sent"
    ERROR = "error"
    DUPLICATE = "duplicate"

class Department(Enum):
    """University departments"""
    MUSIC = "music"
    KOREAN = "korean"
    ENGLISH = "english"
    LIBERAL = "liberal"
    ART = "art"
    EDUCATION = "education"
    GENERAL = "general"

@dataclass
class Article:
    """
    Unified article data model for university admission announcements
    
    All scrapers must convert their data to this format for consistency
    """
    # Required fields
    id: str
    title: str
    url: str
    source: str
    scraped_at: datetime = field(default_factory=datetime.now)
    
    # Content fields
    content: str = ""
    excerpt: str = ""
    
    # Categorization fields
    department: Optional[Department] = None
    university: Optional[str] = None
    program_name: Optional[str] = None
    
    # Date fields
    published_date: Optional[datetime] = None
    deadline: Optional[datetime] = None
    application_start: Optional[datetime] = None
    application_end: Optional[datetime] = None
    
    # Status and metadata
    status: ArticleStatus = ArticleStatus.NEW
    metadata: Dict[str, Any] = field(default_factory=dict)
    tags: List[str] = field(default_factory=list)
    
    def __post_init__(self):
        """Post-initialization processing"""
        # Ensure excerpt is set if content exists but excerpt doesn't
        if self.content and not self.excerpt:
            self.excerpt = self.content[:200] + "..." if len(self.content) > 200 else self.content
        
        # Convert string department to Department enum if needed
        if isinstance(self.department, str):
            try:
                self.department = Department(self.department.lower())
            except ValueError:
                self.department = Department.GENERAL
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert Article to dictionary for JSON serialization
        
        Returns:
            Dictionary representation of the article
        """
        data = asdict(self)
        
        # Convert datetime objects to ISO format strings
        datetime_fields = ['scraped_at', 'published_date', 'deadline', 
                          'application_start', 'application_end']
        
        for field in datetime_fields:
            if field in data and data[field] is not None:
                if isinstance(data[field], datetime):
                    data[field] = data[field].isoformat()
        
        # Convert enums to their values
        if 'department' in data and data['department']:
            data['department'] = data['department'].value if isinstance(data['department'], Department) else data['department']
        
        if 'status' in data:
            data['status'] = data['status'].value
        
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Article':
        """
        Create Article from dictionary (reverse of to_dict())
        
        Args:
            data: Dictionary representation of article
            
        Returns:
            Article instance
        """
        # Handle datetime fields
        datetime_fields = ['scraped_at', 'published_date', 'deadline',
                          'application_start', 'application_end']
        
        for field in datetime_fields:
            if field in data and data[field]:
                if isinstance(data[field], str):
                    data[field] = datetime.fromisoformat(data[field].replace('Z', '+00:00'))
        
        # Handle enum fields
        if 'department' in data and data['department']:
            if isinstance(data['department'], str):
                try:
                    data['department'] = Department(data['department'].lower())
                except ValueError:
                    data['department'] = Department.GENERAL
        
        if 'status' in data and isinstance(data['status'], str):
            data['status'] = ArticleStatus(data['status'])
        
        # Remove any extra fields not in the dataclass
        valid_fields = {f.name for f in field(cls)}
        filtered_data = {k: v for k, v in data.items() if k in valid_fields}
        
        return cls(**filtered_data)
    
    def to_json(self) -> str:
        """
        Convert Article to JSON string
        
        Returns:
            JSON string representation
        """
        return json.dumps(self.to_dict(), ensure_ascii=False, indent=2)
    
    @classmethod
    def from_json(cls, json_str: str) -> 'Article':
        """
        Create Article from JSON string
        
        Args:
            json_str: JSON string representation
            
        Returns:
            Article instance
        """
        data = json.loads(json_str)
        return cls.from_dict(data)
    
    def is_valid(self) -> bool:
        """
        Validate that article has required fields
        
        Returns:
            True if article is valid, False otherwise
        """
        required_fields = ['id', 'title', 'url', 'source']
        for field in required_fields:
            if not getattr(self, field, None):
                return False
        return True
    
    def get_department_emoji(self) -> str:
        """
        Get emoji for the article's department
        
        Returns:
            Emoji string for the department
        """
        emoji_map = {
            Department.MUSIC: "🎵",
            Department.KOREAN: "📚",
            Department.ENGLISH: "🔤", 
            Department.LIBERAL: "📖",
            Department.ART: "🎨",
            Department.EDUCATION: "👨‍🏫",
            Department.GENERAL: "🎓"
        }
        return emoji_map.get(self.department, "🎓")
    
    def get_telegram_message(self, include_content: bool = True) -> str:
        """
        Format article for Telegram message
        
        Args:
            include_content: Whether to include article content
            
        Returns:
            Formatted Telegram message
        """
        emoji = self.get_department_emoji()
        
        message = f"{emoji} <b>[새 입학 공고] {self.title}</b>\n\n"
        
        if self.university:
            message += f"🏫 <b>대학교</b>: {self.university}\n"
        
        if self.department:
            dept_name = self.department.value.upper() if isinstance(self.department, Department) else self.department
            message += f"📌 <b>부서/학과</b>: {dept_name}\n"
        
        if self.deadline:
            message += f"📅 <b>마감일</b>: {self.deadline.strftime('%Y-%m-%d')}\n"
        
        if include_content and self.excerpt:
            message += f"📝 <b>내용</b>: {self.excerpt}\n"
        
        message += f"🔗 <b>링크</b>: {self.url}\n"
        
        # Add hashtags
        tags = ["#대학입시"]
        if self.department:
            tags.append(f"#{self.department.value}")
        if self.university:
            # Create simple hashtag from university name (Korean/English)
            uni_tag = ''.join(e for e in self.university if e.isalnum())
            tags.append(f"#{uni_tag}")
        
        message += f"\n{' '.join(tags)}"
        
        return message
