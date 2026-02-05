#!/bin/bash
# Secure GitHub setup - DO NOT SHARE OUTPUT

echo "🔧 GitHub Secure Setup"
echo "====================="
echo "WARNING: Keep this information private!"
echo ""

# Revoke old token first
echo "⚠️  First, revoke any old tokens at:"
echo "   https://github.com/settings/tokens"
echo ""

# Get new token securely
read -p "Enter your GitHub username: " USERNAME
read -sp "Enter your NEW GitHub token (hidden): " TOKEN
echo

# Validate token format (starts with ghp_ or github_pat_)
if [[ ! "$TOKEN" =~ ^(ghp_|github_pat_) ]]; then
    echo "❌ Invalid token format. Should start with ghp_ or github_pat_"
    exit 1
fi

# Store token with maximum security
echo "$TOKEN" > .github_token
chmod 600 .github_token  # Only you can read/write

# Store username separately
echo "GITHUB_USERNAME='$USERNAME'" > push_config.txt
chmod 644 push_config.txt

echo ""
echo "✅ Setup complete!"
echo "🔐 Token saved to: .github_token (permissions: 600 - only you can read)"
echo "👤 Username saved to: push_config.txt"
echo ""
echo "📋 Next steps:"
echo "1. Run: ./push_to_github.sh"
echo "2. Check: https://github.com/$USERNAME/uni_monitoring.kr"
echo ""
echo "⚠️  IMPORTANT:"
echo "   - Never commit .github_token"
echo "   - Never share your token"
echo "   - Revoke token if compromised"
