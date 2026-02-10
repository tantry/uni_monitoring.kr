================================================================================
UNIVERSITY MONITOR - ZERO NOTIFICATIONS DIAGNOSTIC & FIX GUIDE
================================================================================

📊 PROBLEM ANALYSIS
================================================================================

SYMPTOMS:
- Monitor scrapes 26 articles successfully
  • 4 from Adiga
  • 2 from Seoul Cyber University  
  • 20 from Pusan Nat'l University
- Filtering appears to work (articles get departments assigned)
- But test mode shows: "Would send 0 notifications"

DATABASE STATE:
- 24 articles in "general" department (from 2 sources)
- 2 articles in "student_affairs" department (from 1 source)
- Total: 26 articles already in database

ROOT CAUSE:
All 26 scraped articles are DUPLICATES - they were already processed in a 
previous run and exist in data/state.db. The monitoring flow is:

1. Scrape articles ✓
2. Filter articles (assign departments) ✓
3. Check if duplicate (is_duplicate returns True for all 26) ✓
4. Skip duplicates → new_articles list stays EMPTY ✓
5. "Would send 0 notifications" ✗

SECONDARY ISSUE:
Your monitor_engine.py uses SIMPLE keyword matching, but filters.yaml has
sophisticated confidence thresholds that are IGNORED:

filters.yaml:
  matching:
    min_confidence: 0.10
  departments:
    student_affairs:
      confidence_threshold: 0.05   ← NOT USED!
      
monitor_engine.py filter_article():
  for keyword in keywords:
    if keyword.lower() in text:
      return department  ← Simple substring match only!


================================================================================
🔧 SOLUTIONS (Choose One)
================================================================================

SOLUTION A: IMMEDIATE TEST (Clear Database)
────────────────────────────────────────────────────────────────────────────
Test if filtering works with fresh articles.

STEPS:
1. Run the test script:
   bash test_fresh_scraping.sh
   
2. This will:
   - Backup existing database
   - Clear database
   - Run monitor in test mode
   - Show if articles now trigger notifications

EXPECTED RESULT:
   If filtering works: "Would send N notifications" (N > 0)
   If still broken: "Would send 0 notifications" → keywords don't match

WHEN TO USE:
- Quick diagnostic to confirm filtering logic works
- Safe (creates backup first)
- Doesn't fix the confidence threshold issue


SOLUTION B: ADD DEBUG LOGGING (See What's Happening)
────────────────────────────────────────────────────────────────────────────
Add detailed logging to see which keywords match.

STEPS:
1. Open core/monitor_engine.py
2. Find the filter_article method
3. Replace it with the enhanced version in debug_filter_method.py
4. Run: python3 core/monitor_engine.py --test 2>&1 | grep -A 10 "Filtering"

EXPECTED OUTPUT:
   --- Filtering Article ---
   Title: 2025학년도 신입생 모집...
     ✓ student_affairs: matched 2 keywords: ['공고', '안내']
     ✓ business: matched 1 keywords: ['모집']
     → Assigned to: student_affairs

WHEN TO USE:
- Need to see WHY articles get assigned to departments
- Debugging which keywords are triggering
- Understanding why some articles are "general"


SOLUTION C: PROPER FIX (Confidence-Based Filtering)
────────────────────────────────────────────────────────────────────────────
Implement proper confidence threshold filtering that respects filters.yaml.

STEPS:
1. Open core/monitor_engine.py
2. Replace load_filters() method with load_filters_with_config()
   (from confidence_based_filter.py)
3. Replace filter_article() method with filter_article_with_confidence()
   (from confidence_based_filter.py)
4. Update run() method to use new signatures:
   
   OLD:
   department_filters = self.load_filters()
   ...
   department = self.filter_article(article, department_filters)
   
   NEW:
   filters, configs, min_conf = self.load_filters_with_config()
   ...
   department = self.filter_article_with_confidence(
       article, filters, configs, min_conf
   )

BENEFITS:
- Respects confidence_threshold from filters.yaml
- Uses per-department thresholds (0.05 for student_affairs, 0.15 for others)
- Priority-based selection when multiple departments match
- Better debug logging
- Only assigns "general" when no match meets threshold

WHEN TO USE:
- For robust, production-ready filtering
- When you want to tune thresholds per department
- After confirming basic filtering works (Solution A)


================================================================================
📋 RECOMMENDED WORKFLOW
================================================================================

STEP 1: Confirm the Duplicate Issue
────────────────────────────────────
Run: bash test_fresh_scraping.sh

EXPECTED: You should now see "Would send N notifications" where N = number
          of articles that match your filter keywords.

If you see N > 0: ✓ Filtering works! Problem was duplicates.
If you see N = 0: ✗ No articles match keywords. Proceed to Step 2.


STEP 2: Debug Keyword Matching
────────────────────────────────
If Step 1 showed N = 0:

1. Add debug logging (Solution B)
2. Run: python3 core/monitor_engine.py --test 2>&1 | tee debug_output.txt
3. Look for "Filtering Article" sections
4. Check which keywords match (if any)

POSSIBLE ISSUES:
- Article content doesn't contain expected keywords
- Keywords in filters.yaml don't match actual article language
- Articles are in wrong language/format


STEP 3: Implement Proper Filtering
────────────────────────────────────
Once basic filtering works:

1. Implement Solution C (confidence-based filtering)
2. Tune thresholds in config/filters.yaml:
   - Lower threshold → more articles matched (more false positives)
   - Higher threshold → fewer articles matched (more false negatives)
   
EXAMPLE TUNING:
   student_affairs:
     confidence_threshold: 0.05  ← Very sensitive (1 keyword match)
   
   music:
     confidence_threshold: 0.20  ← More strict (20% of keywords must match)


STEP 4: Test in Production
────────────────────────────
1. Run without --test flag:
   python3 core/monitor_engine.py
   
2. Check Telegram for actual notifications
3. Verify message formatting and links work
4. Monitor logs for any errors


================================================================================
🎯 UNDERSTANDING CONFIDENCE THRESHOLDS
================================================================================

CURRENT SIMPLE MATCHING:
  if "공고" in text:
    return "student_affairs"  ← First match wins
    
CONFIDENCE-BASED MATCHING:
  student_affairs keywords: ["공지사항", "소식", "안내", "공고", "알림", "학사"]
  
  Article contains: "공고" and "안내"
  Matches: 2 out of 6 keywords
  Confidence: 2/6 = 0.33 (33%)
  Threshold: 0.05 (5%)
  Result: 0.33 >= 0.05 → MATCH! ✓

BENEFITS:
- Prevents single-keyword false positives
- Allows tuning per department
- More reliable for production use


================================================================================
📁 FILES CREATED
================================================================================

1. diagnose_monitor.py
   - Analyzes current system state
   - Shows database contents
   - Explains the duplicate issue

2. test_fresh_scraping.sh
   - Clears database (with backup)
   - Tests monitor with fresh articles
   - Quick diagnostic

3. debug_filter_method.py
   - Enhanced filter_article with debug logging
   - Shows which keywords match
   - Helps tune filters

4. confidence_based_filter.py
   - Proper confidence threshold implementation
   - Respects filters.yaml configuration
   - Production-ready solution


================================================================================
❓ FAQ
================================================================================

Q: Why do I have 26 articles in the database but still get 0 notifications?
A: Those 26 articles were already processed. The monitor only sends 
   notifications for NEW articles (not duplicates).

Q: How do I force re-notification of existing articles?
A: Clear the database (Solution A) or delete specific hashes from state.db.
   NOT recommended for production.

Q: Why doesn't monitor_engine use FilterEngine?
A: Different implementations. monitor_engine has its own simple filtering.
   FilterEngine is more sophisticated but not currently integrated.

Q: Should I lower all thresholds to 0.01?
A: No! Lower thresholds = more false positives. Start with:
   - 0.05 for broad categories (student_affairs, general notices)
   - 0.15 for specific departments (music, accounting, etc.)

Q: What if I want ALL articles regardless of keywords?
A: Set all confidence_threshold values to 0.0, or modify filter_article
   to return a specific department instead of "general".


================================================================================
🚀 NEXT STEPS AFTER FIX
================================================================================

1. Monitor for 24-48 hours to verify notifications work
2. Tune confidence thresholds based on false positive/negative rates
3. Add more departments to filters.yaml as needed
4. Consider implementing FilterEngine integration for advanced features
5. Set up systemd service for automatic monitoring (see docs/)


================================================================================
