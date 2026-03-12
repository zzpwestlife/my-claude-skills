#!/usr/bin/env python3
"""
Finalize the document: update markdown with local images and convert to docx
"""
import os
import sys
import re
import hashlib
import subprocess
from pathlib import Path

def get_local_filename(url):
    """Generate local filename from URL"""
    url_hash = hashlib.md5(url.encode('utf-8')).hexdigest()
    ext = '.png' if 'format=png' in url else '.jpg'
    return f"assets/{url_hash}{ext}"

def update_markdown_with_local_images(md_file):
    """Update markdown to use local image paths"""
    with open(md_file, 'r', encoding='utf-8') as f:
        content = f.read()

    # Replace image format from [![Image](url)](link) to ![](local_path)
    def replace_image(match):
        url = match.group(1)
        local_path = get_local_filename(url)
        return f'![]({local_path})'

    pattern = r'\[!\[Image\]\((https://pbs\.twimg\.com/[^)]+)\)\]\([^)]+\)'
    content = re.sub(pattern, replace_image, content)

    # Create new filename with _local suffix
    output_file = md_file.replace('.md', '_local.md')
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(content)

    # Count images
    image_count = len(re.findall(r'!\[\]\(assets/', content))

    print(f"✓ Updated markdown with local images: {output_file}")
    print(f"✓ Total images linked: {image_count}")

    return output_file

def convert_to_docx(md_file, converter_script):
    """Convert markdown to docx using the md_converter script"""
    try:
        result = subprocess.run(
            ['python', converter_script, md_file],
            capture_output=True,
            text=True,
            check=True
        )
        print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ Conversion failed: {e.stderr}")
        return False

def main():
    if len(sys.argv) < 2:
        print("Usage: python finalize_document.py <output_dir>")
        sys.exit(1)

    output_dir = Path(sys.argv[1])

    # Find the most recently modified original markdown file (exclude _local.md files)
    md_files = [f for f in output_dir.glob("*.md") if not f.name.endswith('_local.md')]
    if not md_files:
        print(f"Error: No markdown files found in {output_dir}")
        sys.exit(1)

    # Sort by modification time, newest first
    md_file = sorted(md_files, key=lambda f: f.stat().st_mtime, reverse=True)[0]
    print(f"Processing: {md_file}\n")

    # Update markdown with local images
    local_md_file = update_markdown_with_local_images(str(md_file))

    # Find the converter script (should be in src/md_converter.py)
    converter_script = output_dir.parent / "src" / "md_converter.py"

    if not converter_script.exists():
        print(f"\n⚠️  Converter script not found at {converter_script}")
        print("Please convert manually or provide the correct path")
        sys.exit(1)

    # Convert to docx
    print(f"\nConverting to Word document...")
    if convert_to_docx(local_md_file, str(converter_script)):
        print("\n✅ Document finalized successfully!")
        docx_file = local_md_file.replace('.md', '.docx')
        print(f"📄 Word document: {docx_file}")
    else:
        print("\n⚠️  Conversion to docx failed")
        sys.exit(1)

if __name__ == "__main__":
    main()
