#!/bin/bash
echo "Cleaning up before git commit..."

# Remove temporary/test files
rm -f fix_broken_links.py uni_monitor_fixed.py apply_fix.py 2>/dev/null
rm -f uni_monitor_before_fix.py uni_monitor_backup*.py 2>/dev/null
rm -f test_correct_links.py test_links_properly.py 2>/dev/null
rm -f test_redirect_follow.py test_full_page_access.py 2>/dev/null
rm -f investigate_500_error.py find_correct_link_format.py 2>/dev/null
rm -f add_korean_filter.py 2>/dev/null
rm -f *.log 2>/dev/null

# Keep important files:
# - test_adiga_links.py (useful for debugging)
# - quick_recovery.sh (useful for new chats)
# - All .md files

echo "Cleanup complete. Current files:"
ls -la *.py *.sh *.md
