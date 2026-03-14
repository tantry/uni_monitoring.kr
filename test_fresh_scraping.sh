#!/bin/bash
# Clear database and test monitor with fresh articles

cd /home/bushgrad/uni_monitoring.kr

echo "=== CLEARING DATABASE FOR FRESH TEST ==="
echo ""

# Backup existing database
if [ -f data/state.db ]; then
    echo "📦 Backing up existing database..."
    cp data/state.db data/state.db.backup.$(date +%Y%m%d_%H%M%S)
    echo "✓ Backup created"
fi

# Clear database
echo ""
echo "🗑️  Clearing database..."
rm -f data/state.db
echo "✓ Database cleared"

# Test scraping
echo ""
echo "=== TESTING MONITOR (TEST MODE) ==="
echo ""
python3 core/monitor_engine.py --test

echo ""
echo "=== RESULT ==="
echo "If you see 'Would send N notifications' where N > 0, then filtering is working!"
echo "If you still see 0 notifications, then the articles don't match ANY filter keywords."
echo ""
echo "To restore backup: cp data/state.db.backup.* data/state.db"
