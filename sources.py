# sources.py - Source display configuration
"""
Module for consistent source display across all scrapers
"""

SOURCE_CONFIG = {
    'jinhaksa': {
        'icon': '📘',
        'name': '진학사',
        'short': 'JIN',
        'english': 'Jinhak',
        'url_domain': 'jinhak.com',
        'color': '#1E88E5',
        'priority': 1,
        'reliability': 'high'
    },
    'uway': {
        'icon': '📗',
        'name': 'Uway',
        'short': 'UWAY',
        'english': 'Uway',
        'url_domain': 'uway.com',
        'color': '#43A047',
        'priority': 2,
        'reliability': 'high'
    },
    'unn': {
        'icon': '📰',
        'name': 'U뉴스',
        'short': 'UNN',
        'english': 'UNN News',
        'url_domain': 'news.unn.net',
        'color': '#FB8C00',
        'priority': 3,
        'reliability': 'medium'
    },
    'adigo': {
        'icon': '📕',
        'name': 'Adigo',
        'short': 'ADI',
        'english': 'Adigo',
        'url_domain': 'adiga.kr',
        'color': '#E53935',
        'priority': 4,
        'reliability': 'very_high'
    },
    'edaero': {
        'icon': '📓',
        'name': '이데아로',
        'short': 'EDA',
        'english': 'Edaero',
        'url_domain': 'edaero.com',
        'color': '#8E24AA',
        'priority': 5,
        'reliability': 'medium'
    }
}

MUSIC_TYPES = {
    'classical': {
        'icon': '🎻',
        'name': '클래식',
        'english': 'Classical',
        'keywords': ['클래식', '성악', '오케스트라', '관현악', '피아노', '바이올린']
    },
    'applied_contemporary': {
        'icon': '🎸',
        'name': '실용음악',
        'english': 'Applied/Contemporary',
        'keywords': ['실용음악', '재즈', '편곡', '음향', '미디', '공연제작']
    },
    'vocal_specialized': {
        'icon': '🎤',
        'name': '보컬전문',
        'english': 'Vocal Specialized',
        'keywords': ['보컬', '성악', '가창', '노래', '보컬재즈', 'R&B', '알앤비']
    },
    'instrumental': {
        'icon': '🎹',
        'name': '기악',
        'english': 'Instrumental',
        'keywords': ['기악', '악기', '피아노', '기타', '베이스', '드럼']
    },
    'general': {
        'icon': '🎵',
        'name': '음악일반',
        'english': 'General Music',
        'keywords': ['음악', '음악학과', '음악대학']
    }
}

def get_source_display(source_id):
    return SOURCE_CONFIG.get(source_id, {
        'icon': '📄',
        'name': source_id,
        'short': source_id[:3].upper(),
        'url_domain': 'unknown'
    })

def format_source_line(source_id, university):
    source = get_source_display(source_id)
    return f"{source['icon']} **{source['name']}** `[{source['short']}]` | {university}"

def get_music_types(text):
    text_lower = text.lower()
    detected_types = []
    
    for type_id, config in MUSIC_TYPES.items():
        if any(keyword in text_lower for keyword in config['keywords']):
            detected_types.append(type_id)
    
    if not detected_types and any(word in text_lower for word in MUSIC_TYPES['general']['keywords']):
        detected_types.append('general')
    
    return detected_types

def get_music_icons(type_ids):
    icons = []
    for type_id in type_ids:
        if type_id in MUSIC_TYPES:
            icons.append(MUSIC_TYPES[type_id]['icon'])
    return ' '.join(icons) if icons else '🎵'

def get_music_names(type_ids):
    names = []
    for type_id in type_ids:
        if type_id in MUSIC_TYPES:
            names.append(MUSIC_TYPES[type_id]['name'])
    return ' • '.join(names) if names else '음악'
