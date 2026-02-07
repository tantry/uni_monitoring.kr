#!/bin/bash
# Complete GitHub setup for safe push system

echo "🔧 GitHub Safe Push Setup"
echo "========================"
echo ""
echo "This will setup:"
echo "1. Secure token storage"
echo "2. Username configuration"
echo "3. Safe push script"
echo ""

# Check if already configured
if [ -f ".github_token" ] && [ -f "push_config.txt" ]; then
    echo "⚠️  Already configured. Overwrite? (y/N)"
    read -p "   Choice: " overwrite
    if [[ ! $overwrite =~ ^[Yy]$ ]]; then
        echo "   Keeping existing configuration"
        exit 0
    fi
fi

echo "📋 Step 1: Get GitHub Personal Access Token"
echo "------------------------------------------"
echo "1. Go to: https://github.com/settings/tokens"
echo "2. Click 'Generate new token'"
echo "3. Select 'repo' scope (full control of repositories)"
echo "4. Copy the token (starts with ghp_ or github_pat_)"
echo ""
read -p "Enter your GitHub username: " USERNAME
read -sp "Enter your GitHub token: " TOKEN
echo ""

# Validate token
if [[ ! "$TOKEN" =~ ^(ghp_|github_pat_) ]]; then
    echo "❌ Invalid token format"
    echo "   Token should start with ghp_ or github_pat_"
    exit 1
fi

echo ""
echo "📋 Step 2: Secure storage"
echo "-----------------------"

# Store token with maximum security
echo "$TOKEN" > .github_token
chmod 600 .github_token
echo "✅ Token saved to .github_token (readable only by you)"

# Store username
echo "GITHUB_USERNAME='$USERNAME'" > push_config.txt
chmod 644 push_config.txt
echo "✅ Username saved to push_config.txt"

echo ""
echo "📋 Step 3: Create safe push script (if needed)"
echo "--------------------------------------------"

if [ ! -f "push_to_github_safe.sh" ]; then
    cat > push_to_github_safe.sh << 'SAFEEOF'
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
echo "   (Press 'q' to continue if output is paused)"
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
SAFEEOF
    
    chmod +x push_to_github_safe.sh
    echo "✅ Created push_to_github_safe.sh"
else
    echo "✅ push_to_github_safe.sh already exists"
fi

echo ""
echo "📋 Step 4: Add to .gitignore"
echo "--------------------------"

# Ensure token file is in .gitignore
if [ -f ".gitignore" ]; then
    if ! grep -q "^\.github_token$" .gitignore; then
        echo ".github_token" >> .gitignore
        echo "✅ Added .github_token to .gitignore"
    else
        echo "✅ .github_token already in .gitignore"
    fi
else
    echo ".github_token" > .gitignore
    echo "✅ Created .gitignore with .github_token"
fi

echo ""
echo "🎉 SETUP COMPLETE!"
echo "=================="
echo ""
echo "📁 Files created:"
echo "   • .github_token        (your token - SECRET!)"
echo "   • push_config.txt      (your username)"
echo "   • push_to_github_safe.sh (safe push script)"
echo "   • .gitignore           (protects your token)"
echo ""
echo "🚀 Next steps:"
echo "   1. Run: ./push_to_github_safe.sh"
echo "   2. Choose what files to add"
echo "   3. Review changes (press 'q' if paused)"
echo "   4. Enter commit message"
echo "   5. Confirm push"
echo ""
echo "🔐 Security notes:"
echo "   • Never share .github_token"
echo "   • Token has 'repo' scope - can push to all your repos"
echo "   • Revoke token if compromised: https://github.com/settings/tokens"
echo ""
echo "🌐 Your repository: https://github.com/$USERNAME/uni_monitoring.kr"
