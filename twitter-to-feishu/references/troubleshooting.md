# Troubleshooting Guide

## Common Issues and Solutions

### Issue: Images fail to download with curl/requests

**Symptom:** Connection timeout errors when downloading Twitter images directly

**Root Cause:** Twitter's CDN (pbs.twimg.com) may block direct HTTP requests from certain IPs or require browser-like behavior

**Solution:** Use Playwright to download images instead of curl/requests. Playwright simulates a real browser, bypassing connection restrictions.

```python
# ✗ WRONG - Direct HTTP request often fails
response = requests.get(image_url, timeout=5)

# ✓ CORRECT - Use Playwright
async with async_playwright() as p:
    browser = await p.chromium.launch(headless=True)
    page = await browser.new_page()
    await page.goto(image_url)
    await page.screenshot(path=filepath)
```

### Issue: Images show as "[Image not found]" in docx

**Symptom:** Word document shows placeholder text instead of images

**Root Cause:** Markdown references online URLs instead of local files

**Solution:** Update markdown to use local image paths before converting to docx

```python
# Replace online URLs with local paths
pattern = r'\[!\[Image\]\((https://pbs\.twimg\.com/[^)]+)\)\]\([^)]+\)'
content = re.sub(pattern, lambda m: f'![]({get_local_filename(m.group(1))})', content)
```

### Issue: Playwright installation fails

**Symptom:** `playwright: command not found` or browser download errors

**Solution:** Install Playwright and browsers

```bash
pip install playwright
playwright install chromium
```

### Issue: Image quality is poor

**Symptom:** Downloaded images are low resolution

**Solution:** Use `name=large` or `name=orig` instead of `name=small` in image URLs

```python
# Convert small to large
url = url.replace('name=small', 'name=large')
```

### Issue: Markdown to docx conversion fails

**Symptom:** `md_converter.py` not found or conversion errors

**Solution:** Ensure the web-content-extractor project structure is intact with `src/md_converter.py`

### Issue: Some images still fail to download

**Symptom:** Playwright succeeds for most images but some still fail

**Possible Causes:**
1. Image was deleted from Twitter
2. Network timeout (increase timeout in script)
3. Rate limiting (add longer delays between downloads)

**Solution:** Check if image URL is accessible in browser, increase timeout and delays
