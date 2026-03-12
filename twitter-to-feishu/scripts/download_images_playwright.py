#!/usr/bin/env python3
"""
Download Twitter images using Playwright to bypass connection restrictions.
This is the KEY solution to the image download problem.
"""
import os
import sys
import hashlib
import asyncio
import re
from pathlib import Path
from playwright.async_api import async_playwright

def extract_image_urls_from_markdown(md_file):
    """Extract all Twitter image URLs from markdown file"""
    with open(md_file, 'r', encoding='utf-8') as f:
        content = f.read()

    # Find all Twitter image URLs
    pattern = r'https://pbs\.twimg\.com/media/[^\)"\s]+'
    urls = re.findall(pattern, content)

    # Convert to large size for better quality
    urls = [url.replace('name=small', 'name=large') for url in urls]

    return list(set(urls))  # Remove duplicates

def get_local_filename(url):
    """Generate local filename from URL (matching the hash used in markdown)"""
    # Use small URL for hash to match markdown references
    small_url = url.replace('name=large', 'name=small')
    url_hash = hashlib.md5(small_url.encode('utf-8')).hexdigest()
    ext = '.png' if 'format=png' in url else '.jpg'
    return f"{url_hash}{ext}"

async def download_images(md_file, output_dir):
    """Download all images from markdown file using Playwright"""
    assets_dir = Path(output_dir) / "assets"
    assets_dir.mkdir(parents=True, exist_ok=True)

    # Extract URLs from markdown
    image_urls = extract_image_urls_from_markdown(md_file)

    if not image_urls:
        print("⚠️  No Twitter images found in markdown")
        return 0, 0

    print(f"Found {len(image_urls)} images to download\n")

    success = 0
    failed = 0

    async with async_playwright() as p:
        print("Launching browser...")
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
        )
        page = await context.new_page()

        for url in image_urls:
            filename = get_local_filename(url)
            filepath = assets_dir / filename

            # Skip if exists
            if filepath.exists():
                print(f"✓ Already exists: {filename}")
                success += 1
                continue

            try:
                print(f"  Downloading: {url}")

                # Navigate to image URL
                response = await page.goto(url, wait_until="networkidle", timeout=30000)

                if response and response.ok:
                    # Save screenshot of the image
                    await page.screenshot(path=str(filepath), full_page=True)

                    # Verify file was created
                    if filepath.exists() and filepath.stat().st_size > 0:
                        size_kb = filepath.stat().st_size / 1024
                        print(f"✓ Downloaded: {filename} ({size_kb:.1f} KB)")
                        success += 1
                    else:
                        print(f"✗ Failed (empty file): {filename}")
                        filepath.unlink(missing_ok=True)
                        failed += 1
                else:
                    status = response.status if response else 'N/A'
                    print(f"✗ Failed (HTTP {status}): {filename}")
                    failed += 1

            except Exception as e:
                print(f"✗ Failed ({str(e)[:50]}): {filename}")
                filepath.unlink(missing_ok=True)
                failed += 1

            await asyncio.sleep(0.5)

        await browser.close()

    return success, failed

def main():
    if len(sys.argv) < 2:
        print("Usage: python download_images_playwright.py <output_dir>")
        sys.exit(1)

    output_dir = sys.argv[1]

    # Find the most recently modified markdown file
    md_files = list(Path(output_dir).glob("*.md"))
    if not md_files:
        print(f"Error: No markdown files found in {output_dir}")
        sys.exit(1)

    # Sort by modification time, newest first
    md_file = sorted(md_files, key=lambda f: f.stat().st_mtime, reverse=True)[0]
    print(f"Processing: {md_file}\n")

    # Download images
    success, failed = asyncio.run(download_images(md_file, output_dir))

    print(f"\n{'='*50}")
    print(f"Results: {success} succeeded, {failed} failed")
    print(f"{'='*50}")

    if failed > 0:
        sys.exit(1)

if __name__ == "__main__":
    main()
