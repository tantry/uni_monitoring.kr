Message to assistant:

I'm a new developer onboarding to this university monitoring project. 
reference https://github.com/tantry/uni_monitoring.kr 
I need to add a new RSS feed from https://news.unn.net/rss/allArticle.xml. I have access, but you do not, to the project documentation at docs/. Walk me through the complete integration process using the established patterns and fix any issues we encounter. confirm you are done making initial reconnaisance then i will issue a command to show you my exact file situation 

(User: Start by running this block, copy results, paste into prompt)

```
echo "=== TEST: New developer adding RSS feed ==="
echo "1. They check GUIDE_TO_DOCS.md"
cat docs/GUIDE_TO_DOCS.md | grep -A5 "Getting Started"
echo ""
echo "2. They follow the checklist"
cat docs/UPSCALE_FEED_ADDITION_CHECKLIST.md | grep -E "^### Phase|^- \[ \]"
echo ""
echo "3. They check for common issues"
grep -n "403 Forbidden\|ModuleNotFoundError" docs/UPSCALE_SCRAPER_DEVELOPMENT_GUIDE.md
```
Key Issues to Resolve
   1. Import path resolution (ModuleNotFoundError: 'core')
   2. Factory registration in scraper_factory.py
   3. Testing integration with monitor engine
   4. Department filtering verification
- assist user step-by-step
- base your suggestions only on the facts I provide about my system current state
- stop and allow me to choose an option.
- user prefers execution of exploratory or implementation to working system safely, so do explain the changes to system
- user absolutely prefers sed, cat, cat EOF commands, or nano commands where absolutely required. 

   **NOTE for AI PROMPTS**
(add this at end of every third subsequent prompt)
- assist user step-by-step
- base your suggestions only on the facts I provide about my system current state
- stop and allow me to choose an option.
- user prefers execution of exploratory or implementation to working system safely, so do explain the changes to system
- user absolutely prefers sed, cat, cat EOF commands, or nano commands where absolutely required. 
