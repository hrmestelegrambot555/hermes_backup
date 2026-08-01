# Telegram CDN Image Forwarding Reference

When scraping Telegram channel posts, images are hosted on `cdn4.telesco.pe`. These cannot be sent directly via Bot API URL — they must be downloaded first.

## Problem

```python
# ❌ FAILS: Telegram Bot API rejects external CDN URLs
send_photo(chat_id, "https://cdn4.telesco.pe/file/abc123.jpg", caption)
# Error: "Bad Request: failed to get HTTP URL content"
```

## Solution: Download + Upload

```python
import requests
import os

def download_and_send_image(chat_id, image_url, caption, bot_token):
    """Download image from CDN, then upload to Telegram"""
    # 1. Download with proper headers
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Referer': 'https://t.me/',
    }
    resp = requests.get(image_url, headers=headers, timeout=30)
    resp.raise_for_status()
    
    # 2. Save to temp file
    filepath = "/tmp/temp_image.jpg"
    with open(filepath, 'wb') as f:
        f.write(resp.content)
    
    # 3. Upload to Telegram
    url = f"https://api.telegram.org/bot{bot_token}/sendPhoto"
    with open(filepath, 'rb') as photo:
        files = {'photo': photo}
        data = {'chat_id': chat_id, 'caption': caption[:1024]}
        resp = requests.post(url, files=files, data=data, timeout=30)
    
    # 4. Cleanup
    os.remove(filepath)
    
    return resp.json().get("ok", False)
```

## Finding Image URLs in Scraped HTML

Images are in `background-image` CSS property within `tgme_widget_message_photo` elements:

```python
import re

# Find actual post images (not emoji)
photo_pattern = rf'data-post="{post_id}".*?tgme_widget_message_photo[^>]*background-image:url\([\'"]?([^\'")\s]+)[\'"]?\)'
match = re.search(photo_pattern, html, re.DOTALL)

if match:
    image_url = match.group(1)
    if image_url.startswith('//'):
        image_url = 'https:' + image_url
```

## Filtering Emoji Images

Emoji images from `telegram.org/img/emoji/` must be excluded:

```python
# Skip emoji images
if 'telegram.org/img/emoji' not in url_candidate:
    image_url = url_candidate
```

## Post ID Contains Slash

Post IDs from `data-post` attribute contain slashes (e.g., `takhte_khabar/64369`). Use safe filenames:

```python
safe_id = post_id.replace('/', '_')
filepath = os.path.join(TEMP_DIR, f"{safe_id}.jpg")
```

## Key Learnings

1. **cdn4.telesco.pe images need download+upload** — direct URL forwarding fails
2. **Headers required**: `User-Agent` and `Referer: https://t.me/` to bypass CDN restrictions
3. **Filter emoji images**: Only include images from `tgme_widget_message_photo` elements
4. **Safe filenames**: Replace `/` with `_` in post IDs for file paths
5. **Fallback pattern**: Try download+upload first, fall back to text-only if image fails
