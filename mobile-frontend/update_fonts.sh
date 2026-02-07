#!/bin/bash
# Batch script to replace all Playfair Display font references with Typography.fonts.primary

files=(
  "app/(tabs)/profile.tsx"
  "app/(tabs)/bookmarks.tsx"
  "app/article/[id].tsx"
  "components/ArticleReelCard.tsx"
)

for file in "${files[@]}"; do
  if [ -f "$file" ]; then
    echo "Updating $file..."
    # Replace Playfair Display with Typography.fonts.primary
    sed -i.bak "s/fontFamily: Platform.OS === 'ios' ? 'PlayfairDisplay_700Bold' : 'serif'/fontFamily: Typography.fonts.primary/g" "$file"
    rm "$file.bak"
  fi
done

echo "Batch update complete!"
