#!/bin/bash
# Daily automatic push

echo "📅 Daily Git Push - $(date)"
echo "=========================="

# Run the push script
#./push_to_github.sh
bash

# Add to crontab suggestion
echo ""
echo "💡 To run daily at 9 AM, add to crontab:"
echo "   0 9 * * * cd $(pwd) && ./daily_push.sh >> push.log 2>&1"
