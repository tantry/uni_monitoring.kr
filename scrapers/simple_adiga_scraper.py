#!/usr/bin/env python3
"""
Simple Adiga scraper for testing
"""

class SimpleAdigaScraper:
    """Simple test scraper that returns dummy data"""
    
    def __init__(self):
        self.source_name = "Adiga (Test)"
        self.base_url = "https://adiga.kr"
    
    def fetch_articles(self):
        """Return test articles"""
        return [
            {
                'title': '서울대학교 음악학과 2026년 추가모집 공고',
                'content': '서울대학교 음악학과에서 2026년도 추가모집을 실시합니다. 지원 기간은 2월 15일부터 2월 28일까지입니다.',
                'url': 'https://adiga.kr/article/12345',
                'date': '2026-02-05',
                'source': 'Adiga'
            },
            {
                'title': '연세대학교 영어영문학과 모집안내',
                'content': '연세대학교 영어영문학과에서 신입생 모집을 진행합니다. 서류 접수는 3월 1일부터입니다.',
                'url': 'https://adiga.kr/article/12346',
                'date': '2026-02-05',
                'source': 'Adiga'
            }
        ]
