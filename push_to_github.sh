#!/bin/bash
# Secure GitHub push script

set -e  # Exit on error

# Configuration
TOKEN_FILE=".github_token"
CONFIG_FILE="push_config.txt"
REPO_NAME="uni_monitoring.kr"
DEFAULT_BRANCH="main"

# Check for token
if [ ! -f "$TOKEN_FILE" ]; then
    echo "❌ Token file not found: $TOKEN_FILE"
    echo "   Run: ./setup_github.sh first"
    exit 1
fi

# Read credentials
GITHUB_TOKEN=$(cat "$TOKEN_FILE" | tr -d '[:space:]')
source "$CONFIG_FILE" 2>/dev/null || {
    echo "❌ Config file not found: $CONFIG_FILE"
    exit 1
}

# Validate
if [ -z "$GITHUB_USERNAME" ] || [ -z "$GITHUB_TOKEN" ]; then
    echo "❌ Missing credentials"
    echo "   Run: ./setup_github.sh to setup"
    exit 1
fi

# Initialize git if needed
if [ ! -d ".git" ]; then
    echo "📦 Initializing git repository..."
    git init
    git checkout -b "$DEFAULT_BRANCH" 2>/dev/null || git checkout -b main
fi

# Set remote URL with token
REMOTE_URL="https://${GITHUB_USERNAME}:${GITHUB_TOKEN}@github.com/${GITHUB_USERNAME}/${REPO_NAME}.git"
echo "🔗 Remote: github.com/${GITHUB_USERNAME}/${REPO_NAME}"

# Configure git
git config user.name "$GITHUB_USERNAME"
git config user.email "${GITHUB_USERNAME}@users.noreply.github.com"

# Update remote
git remote remove origin 2>/dev/null || true
git remote add origin "$REMOTE_URL"

# Add files (respects .gitignore)
echo "📁 Adding files..."
git add .

# Commit
COMMIT_MSG="Update: $(date '+%Y-%m-%d %H:%M:%S') - $(hostname)"
if git commit -m "$COMMIT_MSG" 2>/dev/null; then
    echo "💾 Commit: $COMMIT_MSG"
else
    echo "📭 No changes to commit"
    exit 0
fi

# Push
echo "🚀 Pushing to GitHub..."
if git push -u origin "$DEFAULT_BRANCH" 2>/dev/null; then
    echo "✅ Successfully pushed to GitHub!"
    echo "🌐 View at: https://github.com/${GITHUB_USERNAME}/${REPO_NAME}"
else
    # Try alternative branch name
    git push -u origin main --force 2>/dev/null || {
        echo "❌ Push failed. Check:"
        echo "   - Token permissions (needs 'repo' access)"
        echo "   - Internet connection"
        echo "   - Repository exists: https://github.com/${GITHUB_USERNAME}/${REPO_NAME}"
        exit 1
    }
    echo "✅ Pushed to 'main' branch"
fi
