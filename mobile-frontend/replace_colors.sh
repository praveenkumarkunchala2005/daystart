#!/bin/bash

# Comprehensive color replacement script for design system migration

echo "Starting comprehensive color and typography replacement..."

# Define files to update
files=(
  "app/onboarding.tsx"
  "app/edit-interests.tsx"
  "app/article/[id].tsx"
  "app/(tabs)/profile.tsx"
  "app/(tabs)/bookmarks.tsx"
  "components/ArticleReelCard.tsx"
  "components/NewsCard.tsx"
  "components/CustomAlert.tsx"
)

# Background colors
for file in "${files[@]}"; do
  if [ -f "$file" ]; then
    echo "Processing $file..."
    
    # Backgrounds
    sed -i.bak "s/'#000000'/Colors.background/g" "$file"
    sed -i.bak "s/'#000'/Colors.background/g" "$file"
    sed -i.bak "s/'#0F1116'/Colors.background/g" "$file"
    sed -i.bak "s/'#020617'/Colors.background/g" "$file"
    sed -i.bak "s/'#0A0C10'/Colors.background/g" "$file"
    
    # Surfaces
    sed -i.bak "s/'#1C1C1E'/Colors.surface/g" "$file"
    sed -i.bak "s/'#151515'/Colors.surface/g" "$file"
    sed -i.bak "s/'#1a1a1a'/Colors.surface/g" "$file"
    sed -i.bak "s/'#1E293B'/Colors.surface/g" "$file"
    sed -i.bak "s/'#111419'/Colors.surface/g" "$file"
    sed -i.bak "s/'#1A1D23'/Colors.surface/g" "$file"
    
    # Text colors
    sed -i.bak "s/'#94A3B8'/Colors.text.secondary/g" "$file"
    sed -i.bak "s/'#A1A1AA'/Colors.text.secondary/g" "$file"
    sed -i.bak "s/'#64748B'/Colors.text.tertiary/g" "$file"
    sed -i.bak "s/'#71717A'/Colors.text.tertiary/g" "$file"
    sed -i.bak "s/'#8E8E93'/Colors.text.tertiary/g" "$file"
    sed -i.bak "s/'#52525B'/Colors.text.muted/g" "$file"
    sed -i.bak "s/'#C7C7CC'/Colors.text.muted/g" "$file"
    sed -i.bak "s/'#E5E5E5'/Colors.text.primary/g" "$file"
    
    # Borders
    sed -i.bak "s/'#334155'/Colors.borderLight/g" "$file"
    sed -i.bak "s/'#3F3F46'/Colors.borderLight/g" "$file"
    
    # Clean up backup files
    find . -name "*.bak" -delete
  fi
done

echo "Color replacement complete!"
