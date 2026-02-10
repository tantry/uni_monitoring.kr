#!/usr/bin/env python3
"""
Diagnostic script to understand why monitor sends 0 notifications
"""
import sys
sys.path.insert(0, '/home/bushgrad/uni_monitoring.kr')

import yaml
from pathlib import Path

print("=" * 60)
print("MONITORING SYSTEM DIAGNOSTIC")
print("=" * 60)

# 1. Check database location and contents
print("\n1. DATABASE CHECK:")
db_path = Path('/home/bushgrad/uni_monitoring.kr/data/state.db')
if db_path.exists():
    import sqlite3
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()
    
    cursor.execute("SELECT COUNT(*) FROM articles")
    total = cursor.fetchone()[0]
    print(f"   Total articles in DB: {total}")
    
    cursor.execute("SELECT department, COUNT(*) FROM articles GROUP BY department")
    print("   Department breakdown:")
    for dept, count in cursor.fetchall():
        print(f"      {dept}: {count} articles")
    
    # Show recent articles
    cursor.execute("SELECT title, department, source FROM articles ORDER BY id DESC LIMIT 5")
    print("\n   Recent 5 articles:")
    for title, dept, source in cursor.fetchall():
        print(f"      [{dept}] {title[:50]}... (from {source})")
    
    conn.close()
else:
    print(f"   ❌ Database not found at: {db_path}")

# 2. Check filters.yaml
print("\n2. FILTERS.YAML CHECK:")
filters_path = Path('/home/bushgrad/uni_monitoring.kr/config/filters.yaml')
if filters_path.exists():
    with open(filters_path) as f:
        filters = yaml.safe_load(f)
    
    print(f"   Global min_confidence: {filters.get('matching', {}).get('min_confidence', 'NOT SET')}")
    print(f"   Departments configured: {len(filters.get('departments', {}))}")
    
    for dept_id, config in filters.get('departments', {}).items():
        threshold = config.get('confidence_threshold', 'N/A')
        keyword_count = len(config.get('keywords', []))
        print(f"      {dept_id}: {keyword_count} keywords, threshold={threshold}")
else:
    print(f"   ❌ Filters not found at: {filters_path}")

# 3. Check monitor_engine filter logic
print("\n3. MONITOR_ENGINE FILTER LOGIC:")
print("   Current implementation uses SIMPLE keyword matching:")
print("   - Checks if ANY keyword appears in title+content")
print("   - Returns FIRST matching department")
print("   - Returns 'general' if no match")
print("   ⚠️  Does NOT use confidence thresholds from filters.yaml")
print("   ⚠️  Does NOT use FilterEngine class")

# 4. Explain the duplicate issue
print("\n4. DUPLICATE DETECTION ISSUE:")
print("   When monitor runs:")
print("   1. Scrapes articles from sources")
print("   2. Filters each article → assigns department")
print("   3. Checks is_duplicate(article.get_hash())")
print("   4. If duplicate (hash exists in DB) → SKIP")
print("   5. If new → add to new_articles list")
print("   ")
print("   Result: If all scraped articles are ALREADY in DB,")
print("          new_articles list is EMPTY")
print("          → 'Would send 0 notifications'")

# 5. Solutions
print("\n5. SOLUTIONS:")
print("   A. IMMEDIATE FIX (Clear DB for testing):")
print("      rm /home/bushgrad/uni_monitoring.kr/data/state.db")
print("      python3 core/monitor_engine.py --test")
print("   ")
print("   B. PROPER FIX (Use FilterEngine):")
print("      - Modify monitor_engine.py to use FilterEngine")
print("      - FilterEngine uses confidence thresholds properly")
print("      - More sophisticated matching logic")
print("   ")
print("   C. WAIT FOR NEW CONTENT:")
print("      - Current articles are already processed")
print("      - Wait for universities to publish new announcements")
print("      - Monitor will detect and send those")

print("\n" + "=" * 60)
