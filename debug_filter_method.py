#!/usr/bin/env python3
"""
Add this enhanced filter_article method to your monitor_engine.py
This shows EXACTLY what's being matched and why
"""

def filter_article_debug(self, article: Article, filters: Dict[str, List[str]]) -> str:
    """
    Determine which department an article belongs to (WITH DEBUG LOGGING)
    """
    text_to_check = f"{article.title} {article.content}".lower()
    
    self.logger.debug(f"\n--- Filtering Article ---")
    self.logger.debug(f"Title: {article.title[:80]}")
    self.logger.debug(f"Content preview: {article.content[:100]}...")
    
    # Track all matches found
    matches_found = {}
    
    for department, keywords in filters.items():
        matched_keywords = []
        for keyword in keywords:
            if keyword.lower() in text_to_check:
                matched_keywords.append(keyword)
        
        if matched_keywords:
            matches_found[department] = matched_keywords
            self.logger.debug(f"  ✓ {department}: matched {len(matched_keywords)} keywords: {matched_keywords[:3]}")
    
    # Return first match (or "general" if none)
    if matches_found:
        first_match = list(matches_found.keys())[0]
        self.logger.debug(f"  → Assigned to: {first_match}")
        return first_match
    else:
        self.logger.debug(f"  → No matches, assigned to: general")
        return "general"


# USAGE:
# 1. In your monitor_engine.py, replace the filter_article method with this one
# 2. Or add this as a new method and call it instead
# 3. Run with: python3 core/monitor_engine.py --test 2>&1 | grep -A 5 "Filtering Article"

# WHAT YOU'LL SEE:
# --- Filtering Article ---
# Title: 2025학년도 신입생 모집요강 안내
# Content preview: 본교에서는 2025학년도 신입생 모집을 다음과 같이 실시합니다...
#   ✓ student_affairs: matched 2 keywords: ['공고', '안내']
#   ✓ business: matched 1 keywords: ['모집']
#   → Assigned to: student_affairs

