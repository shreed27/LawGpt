#!/bin/bash
# Script to push repository to GitHub

echo "🚀 Pushing Legal Search & Legal-ai to GitHub..."
echo ""

# Check if remote exists
if git remote | grep -q origin; then
    echo "✅ Remote 'origin' already exists"
    git remote -v
else
    echo "⚠️  No remote configured. Please run:"
    echo ""
    echo "git remote add origin https://github.com/YOUR_USERNAME/LawGpt.git"
    echo ""
    echo "Replace YOUR_USERNAME with your GitHub username"
    echo ""
    read -p "Do you want to add remote now? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        read -p "Enter your GitHub username: " GITHUB_USER
        git remote add origin "https://github.com/$GITHUB_USER/LawGpt.git"
        echo "✅ Remote added: https://github.com/$GITHUB_USER/LawGpt.git"
    else
        echo "❌ Please add remote manually and run this script again"
        exit 1
    fi
fi

# Set main branch
git branch -M main

# Push to GitHub
echo ""
echo "📤 Pushing to GitHub..."
git push -u origin main

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Successfully pushed to GitHub!"
    echo ""
    echo "🌐 Your repository is now available at:"
    git remote get-url origin
    echo ""
    echo "📝 Next steps:"
    echo "1. Visit your repository on GitHub"
    echo "2. Add repository description and topics"
    echo "3. Share with your team!"
else
    echo ""
    echo "❌ Push failed. Please check:"
    echo "1. GitHub repository exists"
    echo "2. You have push access"
    echo "3. Remote URL is correct"
fi

