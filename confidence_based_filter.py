#!/usr/bin/env python3
"""
PROPER CONFIDENCE-BASED FILTERING
Replace the filter_article and load_filters methods in monitor_engine.py with these
"""

def load_filters_with_config(self) -> tuple:
    """
    Load department filters WITH confidence configuration
    Returns: (filters_dict, config_dict)
    """
    with open('config/filters.yaml', 'r') as f:
        filters_config = yaml.safe_load(f)
    
    # Extract global config
    global_min_confidence = filters_config.get('matching', {}).get('min_confidence', 0.10)
    
    # Extract department configs
    department_configs = {}
    department_keywords = {}
    
    for dept_id, dept_config in filters_config.get('departments', {}).items():
        department_keywords[dept_id] = dept_config.get('keywords', [])
        department_configs[dept_id] = {
            'name': dept_config.get('name', dept_id),
            'threshold': dept_config.get('confidence_threshold', global_min_confidence),
            'priority': dept_config.get('priority', 99),
            'emoji': dept_config.get('emoji', '📌')
        }
    
    return department_keywords, department_configs, global_min_confidence


def filter_article_with_confidence(self, article: Article, filters: Dict[str, List[str]], 
                                   configs: Dict[str, Dict], min_confidence: float) -> str:
    """
    Filter article using confidence thresholds
    
    Args:
        article: Article to filter
        filters: Department keywords dict
        configs: Department configuration dict
        min_confidence: Global minimum confidence
        
    Returns:
        Department ID or "general"
    """
    text_to_check = f"{article.title} {article.content}".lower()
    
    # Calculate confidence scores for each department
    department_scores = {}
    
    for dept_id, keywords in filters.items():
        dept_config = configs.get(dept_id, {})
        threshold = dept_config.get('threshold', min_confidence)
        priority = dept_config.get('priority', 99)
        
        # Count keyword matches
        matches = sum(1 for kw in keywords if kw.lower() in text_to_check)
        
        # Calculate confidence (matched / total keywords)
        if len(keywords) > 0:
            confidence = matches / len(keywords)
        else:
            confidence = 0.0
        
        # Only consider if meets threshold
        if confidence >= threshold:
            department_scores[dept_id] = {
                'confidence': confidence,
                'priority': priority,
                'matches': matches,
                'total_keywords': len(keywords)
            }
    
    # No matches above threshold
    if not department_scores:
        self.logger.debug(f"No department met threshold for: {article.title[:50]}")
        return "general"
    
    # Select best match: highest confidence, then highest priority (lowest number)
    best_dept = max(
        department_scores.items(),
        key=lambda x: (x[1]['confidence'], -x[1]['priority'])
    )[0]
    
    score = department_scores[best_dept]
    self.logger.debug(
        f"Matched '{best_dept}' with confidence {score['confidence']:.2f} "
        f"({score['matches']}/{score['total_keywords']} keywords)"
    )
    
    return best_dept


# HOW TO USE IN monitor_engine.py:
"""
1. Replace load_filters() with load_filters_with_config()
2. Replace filter_article() with filter_article_with_confidence()
3. Update the run() method:

    # OLD CODE:
    department_filters = self.load_filters()
    ...
    department = self.filter_article(article, department_filters)
    
    # NEW CODE:
    filters, configs, min_conf = self.load_filters_with_config()
    ...
    department = self.filter_article_with_confidence(article, filters, configs, min_conf)
"""

# BENEFITS:
# - Uses confidence thresholds from filters.yaml
# - Per-department thresholds respected
# - Priority-based selection when multiple matches
# - Detailed debug logging
# - Returns "general" only when no match meets threshold

