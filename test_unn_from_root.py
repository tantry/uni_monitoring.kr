#!/usr/bin/env python3
import sys
sys.path.insert(0, '.')

try:
    from scrapers.unn_news_scraper import UNNNewsScraper
    scraper = UNNNewsScraper({'url': 'https://news.unn.net/rss/allArticle.xml'})
    articles = scraper.fetch_articles()
    print(f"Found {len(articles)} articles")
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
