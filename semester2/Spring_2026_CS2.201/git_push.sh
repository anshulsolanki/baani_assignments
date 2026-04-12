#!/bin/bash

# Check if git is initialized
if [ ! -d .git ]; then
    echo "Initializing git repository..."
    git init
fi

# Try to remove existing origin to avoid conflicts, then add it
git remote remove origin 2>/dev/null
echo "Adding remote origin..."
git remote add origin https://github.com/anshulsolanki/baani_assignments.git

# Add all files
echo "Adding files..."
git add .

# Commit changes
echo "Committing changes..."
git commit -m "Complete Assignment 2 (Spring 2026 CS2.201) questions 1, 2, 4, and 5"

# Push to main branch
echo "Pushing to remote..."
git push -u origin main
