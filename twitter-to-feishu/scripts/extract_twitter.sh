#!/bin/bash
# Extract Twitter/X article and convert to Feishu-compatible format
# Usage: ./extract_twitter.sh <twitter_url> [output_dir]

set -e

TWITTER_URL="$1"
OUTPUT_DIR="${2:-output}"

if [ -z "$TWITTER_URL" ]; then
    echo "Error: Twitter URL is required"
    echo "Usage: $0 <twitter_url> [output_dir]"
    exit 1
fi

echo "🚀 Extracting Twitter article..."
echo "   URL: $TWITTER_URL"
echo "   Output: $OUTPUT_DIR"
echo ""

# Step 1: Extract article using main.py
echo "📥 Step 1/3: Fetching article content..."
python main.py "$TWITTER_URL" --output "$OUTPUT_DIR" --debug

# Step 2: Download images using Playwright
echo "🖼️  Step 2/3: Downloading images with Playwright..."
python scripts/download_images_playwright.py "$OUTPUT_DIR"

# Step 3: Update markdown and convert to docx
echo "📄 Step 3/3: Converting to Word document..."
python scripts/finalize_document.py "$OUTPUT_DIR"

echo ""
echo "✅ Complete! Files generated:"
echo "   📝 Markdown: $OUTPUT_DIR/*.md"
echo "   📄 Word Doc: $OUTPUT_DIR/*.docx"
echo "   🖼️  Images: $OUTPUT_DIR/assets/"
echo ""
echo "💡 The .docx file can be directly imported into Feishu (飞书)"
