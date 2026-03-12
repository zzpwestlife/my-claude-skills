---
name: twitter-to-feishu
description: >
  Extract Twitter/X articles and convert to Feishu-compatible Word documents
  with embedded images. Use when user wants to: (1) scrape or extract content
  from Twitter/X URLs (x.com or twitter.com), (2) convert Twitter threads or
  articles to documents, (3) save Twitter content for Feishu/Lark import,
  (4) download Twitter articles with images. Handles image download issues
  using Playwright to bypass connection restrictions.
---

# Twitter to Feishu Converter

Extract Twitter/X articles and convert them to Word documents ready for Feishu import, with all images embedded locally.

## Prerequisites

This skill requires the `web-content-extractor` project to be available. Ensure:

1. The project exists at a known location (e.g., `~/Code/OpenSource/my-trivia-tools/web-content-extractor`)
2. Python virtual environment is set up with dependencies installed
3. Playwright browsers are installed: `playwright install chromium`

## Quick Start

When user provides a Twitter/X URL, follow this workflow:

1. Navigate to the web-content-extractor project directory
2. Run the extraction process (3 steps below)
3. Deliver the final .docx file to the user

## Workflow

### Step 1: Extract Article Content

Use the existing `main.py` to fetch the article:

```bash
cd /path/to/web-content-extractor
python main.py <twitter_url> --output output --debug
```

This creates:
- `output/*.md` - Markdown file with article content
- `output/assets/` - Directory for images (initially empty or incomplete)

### Step 2: Download Images with Playwright

**CRITICAL:** This is the key solution to image download problems.

Twitter's CDN blocks direct HTTP requests (curl/requests fail with timeouts). Use Playwright to download images by simulating a real browser:

```bash
python scripts/download_images_playwright.py output
```

The script:
- Extracts image URLs from the markdown file
- Uses Playwright to download each image (bypasses restrictions)
- Saves images to `output/assets/` with consistent filenames
- Reports success/failure for each image

### Step 3: Finalize Document

Update markdown to use local images and convert to Word:

```bash
python scripts/finalize_document.py output
```

This:
- Creates `*_local.md` with local image references
- Converts to `*_local.docx` using the project's converter
- Embeds all images in the Word document

## Output Files

After completion, the output directory contains:

```
output/
├── Original_Article.md          # Original with online image URLs
├── Original_Article_local.md    # Updated with local image paths
├── Original_Article_local.docx  # Final Word document (for Feishu)
└── assets/                      # All downloaded images
    ├── abc123.jpg
    ├── def456.png
    └── ...
```

**Deliver to user:** The `*_local.docx` file can be directly imported into Feishu.

## Key Technical Details

### Why Playwright for Images?

Direct HTTP requests to `pbs.twimg.com` often fail with connection timeouts because:
- Twitter's CDN may block non-browser requests
- Requires proper User-Agent and headers
- May have rate limiting or IP restrictions

Playwright solves this by:
- Launching a real Chromium browser
- Navigating to each image URL
- Taking a screenshot (captures the image)
- Saving to local file

### Image Filename Consistency

Images are named using MD5 hash of the original URL:

```python
url_hash = hashlib.md5(url.encode('utf-8')).hexdigest()
filename = f"{url_hash}.jpg"  # or .png
```

This ensures:
- Consistent filenames across different scripts
- Markdown references match downloaded files
- No duplicate downloads

### Image Quality

Use `name=large` in URLs for better quality:

```python
url = url.replace('name=small', 'name=large')
```

## Troubleshooting

If images fail to download or other issues occur, see [troubleshooting.md](references/troubleshooting.md) for:
- Connection timeout solutions
- Playwright installation issues
- Image quality problems
- Conversion errors

## Scripts Reference

All scripts are located in the skill's `scripts/` directory:

- **extract_twitter.sh** - Complete workflow wrapper (optional convenience script)
- **download_images_playwright.py** - Core image downloader using Playwright
- **finalize_document.py** - Markdown updater and docx converter

## Example Usage

```bash
# User provides URL
URL="https://x.com/HiTw93/status/2032091246588518683"

# Navigate to project
cd ~/Code/OpenSource/my-trivia-tools/web-content-extractor

# Step 1: Extract
python main.py "$URL" --output output --debug

# Step 2: Download images
python scripts/download_images_playwright.py output

# Step 3: Finalize
python scripts/finalize_document.py output

# Result: output/*_local.docx ready for Feishu
```

## Success Criteria

- All article text extracted correctly
- All images downloaded successfully (23/23 in typical long-form article)
- Word document contains embedded images (not online links)
- File can be imported into Feishu without errors
