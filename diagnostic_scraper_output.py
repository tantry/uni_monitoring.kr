#!/usr/bin/env python3
"""
Diagnostic script to capture EXACTLY what the Adiga scraper is extracting.
Run this in your ~/uni_monitoring.kr directory to see actual output.

This shows:
1. Raw articles extracted
2. What passes/fails filtering
3. Exact content being sent to Telegram
"""

import sys
import json
from datetime import datetime

# Add project to path
sys.path.insert(0, '.')

def run_diagnostic():
    print("=" * 80)
    print("ADIGA SCRAPER DIAGNOSTIC - ACTUAL OUTPUT CAPTURE")
    print("=" * 80)
    print(f"Started: {datetime.now()}\n")
    
    try:
        # Import the scraper
        from scrapers.adiga_scraper import AdigaScraper
        print("✓ Successfully imported AdigaScraper\n")
        
    except ImportError as e:
        print(f"✗ Failed to import scraper: {e}")
        print("\nTroubleshooting:")
        print("1. Make sure you're in ~/uni_monitoring.kr directory")
        print("2. Make sure scrapers/adiga_scraper.py exists")
        return
    
    # Create scraper instance
    print("Initializing scraper...")
    config = {'url': 'https://www.adiga.kr'}
    scraper = AdigaScraper(config)
    print(f"✓ Scraper initialized: {scraper.get_source_name()}\n")
    
    # STEP 1: Fetch raw articles
    print("-" * 80)
    print("STEP 1: FETCH RAW ARTICLES FROM ADIGA")
    print("-" * 80)
    
    articles = scraper.fetch_articles()
    print(f"\n✓ Fetched {len(articles)} articles\n")
    
    if not articles:
        print("⚠ NO ARTICLES FOUND!")
        print("This is a critical issue - scraper returned empty list.")
        return
    
    # Display each article
    print(f"{'#':<3} {'TITLE':<50} {'URL':<60} {'CONTENT LENGTH':<15}")
    print("-" * 130)
    
    for i, article in enumerate(articles, 1):
        title = article.get('title', 'NO TITLE')[:48]
        url = article.get('url', 'NO URL')[:58]
        content = article.get('content', '')
        content_len = len(content)
        
        print(f"{i:<3} {title:<50} {url:<60} {content_len:<15}")
    
    # STEP 2: Show detailed view of first 3 articles
    print("\n" + "-" * 80)
    print("STEP 2: DETAILED VIEW OF FIRST 3 ARTICLES")
    print("-" * 80)
    
    for i, article in enumerate(articles[:3], 1):
        print(f"\n📰 ARTICLE {i}")
        print(f"   Title: {article.get('title', 'NO TITLE')}")
        print(f"   URL: {article.get('url', 'NO URL')}")
        print(f"   Content length: {len(article.get('content', ''))} chars")
        print(f"   Source: {article.get('source', 'unknown')}")
        
        content = article.get('content', '')
        if content:
            preview = content[:200] if len(content) > 200 else content
            print(f"   Content preview: {preview}...")
        else:
            print(f"   Content: [EMPTY]")
    
    # STEP 3: Parse articles (apply department detection)
    print("\n" + "-" * 80)
    print("STEP 3: PARSED ARTICLES (WITH DEPARTMENT DETECTION)")
    print("-" * 80)
    
    parsed_articles = []
    for i, raw in enumerate(articles[:5], 1):  # First 5
        try:
            parsed = scraper.parse_article(raw)
            parsed_articles.append(parsed)
            
            print(f"\n✓ Article {i} parsed:")
            print(f"   Title: {parsed.title}")
            print(f"   Department detected: {parsed.department if hasattr(parsed, 'department') else 'N/A'}")
            print(f"   URL: {parsed.url}")
            
        except Exception as e:
            print(f"\n✗ Article {i} parse failed: {e}")
    
    # STEP 4: Filter analysis
    print("\n" + "-" * 80)
    print("STEP 4: FILTER ANALYSIS")
    print("-" * 80)
    
    try:
        from core.filter_engine import FilterEngine
        filter_engine = FilterEngine()
        
        print(f"\n✓ FilterEngine loaded")
        print(f"   Active filters: {filter_engine.config.get('filters', {}).keys() if hasattr(filter_engine, 'config') else 'Unknown'}\n")
        
        # Test filtering on first 5 articles
        for i, parsed in enumerate(parsed_articles[:5], 1):
            try:
                # Try to apply filters
                result = filter_engine.apply_filters(parsed)
                
                print(f"Article {i}: {parsed.title[:50]}...")
                print(f"  Passes filters: {result}")
                
            except Exception as e:
                print(f"Article {i}: Filter application error: {e}")
    
    except ImportError:
        print("⚠ FilterEngine not available - skipping filter analysis")
    
    # STEP 5: Telegram message simulation
    print("\n" + "-" * 80)
    print("STEP 5: TELEGRAM MESSAGE SIMULATION")
    print("-" * 80)
    print("(This is what WOULD be sent to Telegram)\n")
    
    for i, parsed in enumerate(parsed_articles[:2], 1):  # First 2
        dept = parsed.department if hasattr(parsed, 'department') else 'unknown'
        
        message = f"""
🎓 <b>새 입학 공고</b>

<b>제목:</b> {parsed.title}

<b>학과:</b> {dept}

<b>내용:</b> {parsed.content[:150] if parsed.content else '[내용 없음]'}...

<b>링크:</b> {parsed.url}

<b>출처:</b> {parsed.source}

#adiga #대학입시
"""
        print(f"MESSAGE {i}:")
        print(message)
        print("-" * 80)
    
    # STEP 6: Analysis Summary
    print("\n" + "-" * 80)
    print("STEP 6: ANALYSIS SUMMARY")
    print("-" * 80)
    
    print(f"\nTotal articles extracted: {len(articles)}")
    print(f"Total successfully parsed: {len(parsed_articles)}")
    
    # Analyze content types
    titles_with_keywords = {
        'privacy': sum(1 for a in articles if 'privacy' in (a.get('title', '') or '').lower()),
        'terms': sum(1 for a in articles if 'terms' in (a.get('title', '') or '').lower()),
        'navigation': sum(1 for a in articles if 'menu' in (a.get('title', '') or '').lower()),
        'admission': sum(1 for a in articles if any(k in (a.get('title', '') or '').lower() for k in ['모집', '입학', '입시', 'admission'])),
    }
    
    print("\nArticle type breakdown:")
    for type_name, count in titles_with_keywords.items():
        print(f"  - {type_name}: {count} articles")
    
    # Questions for the user
    print("\n" + "-" * 80)
    print("DIAGNOSTIC QUESTIONS FOR YOU")
    print("-" * 80)
    print("""
1. LOOK AT THE EXTRACTED ARTICLES ABOVE:
   - Are these actual admission announcements or navigation/policy pages?
   
2. DO YOU SEE:
   - Privacy policy or Terms of Service links?
   - Navigation menu items?
   - Non-admission content (sports, events)?
   - Very old announcements?
   
3. WHAT'S THE ACTUAL URL BEING SCRAPED:
   - Is it pointing to the admission announcement section?
   - Or pointing to general website content?
   
4. FOR EACH BAD ARTICLE:
   - Note the exact title
   - Note the URL it's linking to
   - This tells us if we need to:
     a) Change the URL the scraper fetches from
     b) Add better filters
     c) Update the department detection
""")
    
    print("\n" + "=" * 80)
    print("DIAGNOSTIC COMPLETE")
    print("=" * 80)
    print(f"Ended: {datetime.now()}")
    print("\nNext: Share the output above with Claude so we can diagnose")
    print("      what's causing low-value content to be sent.")

if __name__ == "__main__":
    run_diagnostic()
