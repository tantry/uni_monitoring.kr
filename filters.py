#!/usr/bin/env python3
"""
Department filtering for university admission announcements
"""

# Department keywords for filtering
DEPARTMENT_KEYWORDS = {
    'music': ['음악', 'music', '실용음악', '성악', '작곡', '교향곡', '오케스트라'],
    'korean': ['한국어', '국어', '국어국문', '국문학', '한국언어', '한글'],
    'english': ['영어', '영어영문', '영문학', '영미언어', '영미문화'],
    'liberal': ['인문', '인문학', '교양', '교양교육', '자유전공', '기초교육'],
    'art': ['미술', '조형', '디자인', '회화', '공예'],
    'education': ['교육', '교육학', '교원', '교육대학']
}

def filter_by_department(article):
    """
    Determine which department an article belongs to based on keywords
    Returns department name or None if no match
    """
    title = article.get('title', '').lower()
    content = article.get('content', '').lower()
    
    combined_text = title + " " + content
    
    # Check each department's keywords
    for department, keywords in DEPARTMENT_KEYWORDS.items():
        for keyword in keywords:
            if keyword.lower() in combined_text:
                return department
    
    return None

# Legacy function name for backward compatibility
filter_article = filter_by_department
