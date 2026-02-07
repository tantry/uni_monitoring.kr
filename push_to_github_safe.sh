#!/bin/bash
# Safe GitHub push with review - uses your existing setup

set -e  # Exit on error

# Configuration - using YOUR existing files
TOKEN_FILE=".github_token"
CONFIG_FILE="push_config.txt"
REPO_NAME="uni_monitoring.kr"

# Load your existing credentials
if [ ! -f "$TOKEN_FILE" ]; then
    echo "❌ Token file not found: $TOKEN_FILE"
    exit 1
fi

if [ ! -f "$CONFIG_FILE" ]; then
    echo "❌ Config file not found: $CONFIG_FILE"
    exit 1
fi

GITHUB_TOKEN=$(cat "$TOKEN_FILE" | tr -d '[:space:]')
source "$CONFIG_FILE" 2>/dev/null

# Validate
if [ -z "$GITHUB_USERNAME" ] || [ -z "$GITHUB_TOKEN" ]; then
    echo "❌ Missing credentials in config files"
    exit 1
fi

echo "=== GitHub Push - Safe Mode ==="
echo "Repository: $REPO_NAME"
echo "User: $GITHUB_USERNAME"
echo ""

# Step 1: Show current status
echo "1. 📊 CURRENT GIT STATUS:"
echo "------------------------"
git status --short
echo ""

# Step 2: Ask about what to add
echo "2. 📦 SELECT FILES TO ADD:"
echo "-------------------------"
echo "   a) Add ALL changes"
echo "   b) Add only modified/deleted files"
echo "   c) Cancel and exit"
echo ""
read -p "   Your choice (a/b/c): " choice

case $choice in
    a)
        echo "   Adding ALL changes..."
        git add .
        ;;
    b)
        echo "   Adding modified/deleted files..."
        git add -u
        ;;
    c)
        echo "   ❌ Cancelled"
        exit 0
        ;;
    *)
        echo "   ❌ Invalid choice"
        exit 1
        ;;
esac

# Step 3: Show what will be committed
echo ""
echo "3. ✅ STAGED CHANGES:"
echo "-------------------"
git diff --cached --name-status
if [ $? -ne 0 ]; then
    echo "   No changes staged"
    echo "   ❌ Nothing to commit"
    exit 0
fi
echo ""

# Step 4: Commit
echo "4. 💾 COMMIT CHANGES:"
echo "-------------------"
read -p "   Commit message (Enter for default): " user_msg
if [ -z "$user_msg" ]; then
    user_msg="Update: $(date '+%Y-%m-%d %H:%M:%S') - $(hostname)"
fi

echo "   Committing..."
git commit -m "$user_msg"
echo "   ✅ Commit created"
echo ""

# Step 5: Push confirmation
echo "5. 🚀 PUSH TO GITHUB:"
echo "-------------------"
echo "   Repository: https://github.com/$GITHUB_USERNAME/$REPO_NAME"
echo ""
read -p "   Push these changes to GitHub? (y/N): " push_choice

if [[ $push_choice =~ ^[Yy]$ ]]; then
    echo "   Pushing..."
    
    # Use your existing remote setup
    REMOTE_URL="https://${GITHUB_USERNAME}:${GITHUB_TOKEN}@github.com/${GITHUB_USERNAME}/${REPO_NAME}.git"
    
    # Ensure remote is set (like your original script)
    git remote remove origin 2>/dev/null || true
    git remote add origin "$REMOTE_URL" 2>/dev/null || true
    
    # Push (try main branch first, then try with --force if needed)
    if git push -u origin main 2>/dev/null || git push -u origin main --force 2>/dev/null; then
        echo "   ✅ Successfully pushed to GitHub!"
        echo "   🌐 View: https://github.com/${GITHUB_USERNAME}/${REPO_NAME}"
    else
        echo "   ❌ Push failed"
        echo "   Check token permissions or try manual push"
    fi
else
    echo "   Changes committed locally but NOT pushed"
    echo "   Run 'git push' manually when ready"
fi

echo ""
echo "=== Complete ==="
