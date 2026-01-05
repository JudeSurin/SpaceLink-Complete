#!/bin/bash

# OrbitLink Enterprise Gateway - Automated GitHub Setup Script
# This script will help you quickly push the project to GitHub

set -e  # Exit on error

echo "🚀 OrbitLink Enterprise Gateway - GitHub Setup"
echo "=============================================="
echo ""

# Check if git is installed
if ! command -v git &> /dev/null; then
    echo "❌ Git is not installed. Please install git first."
    echo "   Visit: https://git-scm.com/downloads"
    exit 1
fi

# Get GitHub username
echo "📝 GitHub Setup"
read -p "Enter your GitHub username: " GITHUB_USERNAME

if [ -z "$GITHUB_USERNAME" ]; then
    echo "❌ GitHub username is required"
    exit 1
fi

# Repository name
REPO_NAME="orbitlink-enterprise-gateway"

echo ""
echo "✅ Configuration:"
echo "   GitHub Username: $GITHUB_USERNAME"
echo "   Repository Name: $REPO_NAME"
echo "   Repository URL: https://github.com/$GITHUB_USERNAME/$REPO_NAME"
echo ""

# Confirm
read -p "Does this look correct? (y/n): " CONFIRM
if [ "$CONFIRM" != "y" ]; then
    echo "❌ Setup cancelled"
    exit 1
fi

echo ""
echo "📦 Setting up Git repository..."

# Initialize git if not already done
if [ ! -d ".git" ]; then
    git init
    echo "✅ Git repository initialized"
else
    echo "ℹ️  Git repository already exists"
fi

# Add all files
echo "📝 Staging files..."
git add .

# Commit
echo "💾 Creating initial commit..."
git commit -m "feat: Initial release of OrbitLink Enterprise Gateway

- Enterprise API gateway with FastAPI
- Dual authentication (API keys + OAuth2/JWT)
- RBAC with multi-tenant isolation
- Telemetry ingestion and network monitoring
- Partner onboarding workflows
- Python SDK and comprehensive documentation
- Docker deployment support

Tech Stack: FastAPI, SQLAlchemy, Docker, OAuth2, JWT
" || echo "ℹ️  Files already committed"

# Set main branch
git branch -M main

# Add remote
REMOTE_URL="https://github.com/$GITHUB_USERNAME/$REPO_NAME.git"
if git remote | grep -q "origin"; then
    echo "ℹ️  Remote 'origin' already exists, updating..."
    git remote set-url origin "$REMOTE_URL"
else
    echo "🔗 Adding remote repository..."
    git remote add origin "$REMOTE_URL"
fi

echo ""
echo "=============================================="
echo "⚠️  IMPORTANT: Create GitHub Repository First!"
echo "=============================================="
echo ""
echo "Before pushing, you need to create the repository on GitHub:"
echo ""
echo "1. Go to: https://github.com/new"
echo "2. Repository name: $REPO_NAME"
echo "3. Description: Enterprise satellite connectivity integration platform"
echo "4. Choose: Public (recommended for portfolio)"
echo "5. DO NOT initialize with README, .gitignore, or license"
echo "6. Click 'Create repository'"
echo ""
read -p "Press ENTER once you've created the repository on GitHub..."

echo ""
echo "🚀 Pushing to GitHub..."
echo ""

# Push to GitHub
if git push -u origin main; then
    echo ""
    echo "=============================================="
    echo "🎉 SUCCESS! Project pushed to GitHub!"
    echo "=============================================="
    echo ""
    echo "📍 Your repository: https://github.com/$GITHUB_USERNAME/$REPO_NAME"
    echo ""
    echo "Next steps:"
    echo "1. ✅ View your repo: https://github.com/$GITHUB_USERNAME/$REPO_NAME"
    echo "2. 📝 Add repository description and topics on GitHub"
    echo "3. 🏷️  Create a release (v1.0.0)"
    echo "4. 🧪 Test locally: docker-compose up"
    echo "5. 💼 Add to your resume and LinkedIn!"
    echo ""
    echo "🎯 Ready for interviews!"
else
    echo ""
    echo "=============================================="
    echo "⚠️  Push Failed"
    echo "=============================================="
    echo ""
    echo "Common issues:"
    echo ""
    echo "1. Authentication Required:"
    echo "   - Use GitHub CLI: gh auth login"
    echo "   - Or create Personal Access Token:"
    echo "     https://github.com/settings/tokens"
    echo ""
    echo "2. Repository doesn't exist:"
    echo "   - Make sure you created it at: https://github.com/new"
    echo "   - Repository name must be: $REPO_NAME"
    echo ""
    echo "3. Try manual push:"
    echo "   git push -u origin main"
    echo ""
fi

echo ""
echo "📚 For detailed instructions, see: GITHUB_SETUP_GUIDE.md"
