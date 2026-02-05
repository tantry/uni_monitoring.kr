#!/bin/bash
# Quick recovery for University Admission Monitor

echo "🔄 Starting recovery process..."

# Backup current files
echo "📦 Backing up current files..."
timestamp=$(date +%Y%m%d_%H%M%S)
backup_dir="backup_${timestamp}"
mkdir -p "$backup_dir"
cp -f multi_monitor.py "$backup_dir/" 2>/dev/null || true
cp -f state.json "$backup_dir/" 2>/dev/null || true

# Install the fixed version
echo "🔧 Installing fixed monitor..."
cp -f multi_monitor_fixed.py multi_monitor.py

# Test the configuration
echo "🧪 Testing configuration..."
python3 -c "import config; print('✅ Config loaded:', config.BOT_TOKEN[:10] + '...')"

# Clear state to force fresh alerts
echo "🗑️ Clearing state for fresh alerts..."
rm -f state.json

# Run a test
echo "🚀 Running test..."
python3 test_integration.py

echo ""
echo "✅ Recovery complete!"
echo "Next: Run the monitor with: python3 multi_monitor.py"
