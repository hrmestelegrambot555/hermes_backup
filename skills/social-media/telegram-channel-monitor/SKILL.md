---
name: telegram-channel-monitor
description: "Forward important news from Telegram channels via Bot API."
version: 1.0.0
author: hermes-agent
license: MIT
metadata:
  hermes:
    tags: [telegram, news, monitoring, forwarding, cron]
---

# Telegram Channel Monitor & Forwarder

---

## Key Techniques

### 1. Reading Telegram Channels (No API Needed)

Public Telegram channels have a web preview at `https://t.me/s/{channel_username}`:

```python
import re, requests
resp = requests.get(f"https://t.me/s/{channel}")
posts = re.findall(r'data-post="([^"]+)".*?js-message_text[^>]*>(.*?)</div>', resp.text, re.DOTALL)
```

### 2. Telegram Bot API for Sending

**Requirements:**
- Bot token from @BotFather
- Bot must be admin of target channel with "Post Messages" permission

```python
import requests
url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
payload = {
    "chat_id": CHANNEL_ID,
    "text": message_text,
    "parse_mode": "HTML",
    "disable_web_page_preview": True
}
requests.post(url, json=payload)
```

### 3. Filtering Important Content

```python
IMPORTANT_KEYWORDS = ["فوری", "🚨", "‼️", "حمله", "توافق", "آتش‌بس"]
def is_important(text):
    return any(kw.lower() in text.lower() for kw in IMPORTANT_KEYWORDS)
```

### 4. Deduplication

Track sent message IDs to avoid duplicates:
```python
sent_ids = set(load_json("sent_ids.json", {"ids": []})["ids"])
```

### 5. Rate Limiting

- Add `time.sleep(1)` between API calls
- Same chat: ~20 messages/minute

## Two-Tier Filtering

Use strict filtering to avoid noise. Define "important" vs "very important":

```python
def is_important(text):
    """Standard importance - used for logging"""
    keywords = ["فوری", "🚨", "‼️", "حمله", "توافق"]
    return any(kw.lower() in text.lower() for kw in keywords)

def is_very_important(text):
    """Very important - actually forwards to channel"""
    keywords = ["‼️", "🚨", "فوری:", "BREAKING", "حمله موشکی", "بمباران", "توافق", "آتش‌بس"]
    return any(kw.lower() in text.lower() for kw in keywords)
```

## AI-Powered Filtering (Recommended)

For intelligent news filtering (replaces keyword matching):
- `references/ai-news-filtering.md` — OpenRouter integration for AI importance detection + summarization

**Pattern**: Use Google Gemma 4 (free) via OpenRouter to analyze news importance. Two functions:
- `ai_check_importance(text)` → returns True/False
- `ai_summarize(text)` → returns cleaned summary

**Benefits**: Context-aware, catches nuance, reduces noise significantly.

## Minimalist Forwarding

User preference: **text-only, no source attribution, no links.** Just the news.

```python
# ✅ What user wants:
send_to_channel(post["text"])

# ❌ What to avoid:
send_to_channel(f"📢 {source_name}\n\n{post['text']}\n\n🔗 <a href=\"{link}\">مشاهده</a>")
```

When user says "فقط متن اخبار مهم" (only important news text), strip all formatting, links, channel names before sending.

## Scripts

- `scripts/forwarder_template.py` — Basic text-only forwarder template
- `scripts/forwarder_template_with_images.py` — Forwarder with image download + upload support

## AI-Powered Filtering

For intelligent news filtering (recommended over keyword matching):
- `references/ai-news-filtering.md` — OpenRouter integration for AI importance detection + summarization

**Pattern**: Use Google Gemma 4 (free) via OpenRouter to analyze news importance. Two functions:
- `ai_check_importance(text)` → returns True/False
- `ai_summarize(text)` → returns cleaned summary

**Benefits**: Context-aware, catches nuance, reduces noise significantly.

```python
# Quick integration
if ai_check_importance(post["text"]):
    summary = ai_summarize(post["text"])
    send_to_channel(summary)
```

```
cronjob create --schedule "every 30m" --prompt "python3 /path/to/forwarder.py"
```

## Sending Images with News

When forwarding news that includes images, use `sendPhoto` instead of `sendMessage`.

### Extracting Images from Channel Preview

Images are embedded in `tgme_widget_message_photo_wrap` divs with `background-image:url()`:

```python
# Find image for a specific post
img_pattern = rf'data-post="{re.escape(post_id)}".*?background-image:url\([\'"]?([^\'")\s]+)[\'"]?\)'
img_match = re.search(img_pattern, html, re.DOTALL)
if img_match:
    image_url = img_match.group(1)
    if image_url.startswith('//'):
        image_url = 'https:' + image_url
```

### Sending Photo with Caption

```python
def send_photo(chat_id, photo_url, caption):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendPhoto"
    payload = {
        "chat_id": chat_id,
        "photo": photo_url,
        "caption": caption[:1024],  # Telegram caption limit
        "parse_mode": "HTML",
    }
    resp = requests.post(url, json=payload, timeout=30)
    return resp.json().get("ok", False)
```

### Fallback Pattern

Always fall back to text-only if image fails:

```python
if post.get("image_url"):
    success = send_photo(TARGET_CHAT_ID, post["image_url"], post["text"])
    if not success:
        success = send_message(TARGET_CHAT_ID, post["text"])  # fallback
else:
    success = send_message(TARGET_CHAT_ID, post["text"])
```

**Note**: Some channels use CDN URLs (`cdn4.telesco.pe`) that may not be accessible via Bot API. Always implement fallback to text-only.

### Downloading and Uploading Images (Reliable Method)

When direct URL sending fails, download the image first and upload it:

```python
import os

TEMP_DIR = "/tmp/news_images"
os.makedirs(TEMP_DIR, exist_ok=True)

def download_image(url, post_id):
    """Download image to temp file"""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Referer': 'https://t.me/',
        }
        resp = requests.get(url, headers=headers, timeout=30)
        resp.raise_for_status()
        
        # Safe filename (replace / with _)
        safe_id = post_id.replace('/', '_')
        ext = '.jpg'
        if 'png' in resp.headers.get('content-type', ''):
            ext = '.png'
        
        filepath = os.path.join(TEMP_DIR, f"{safe_id}{ext}")
        with open(filepath, 'wb') as f:
            f.write(resp.content)
        
        return filepath
    except Exception as e:
        print(f"  Download error: {e}")
        return None

def send_photo_file(chat_id, filepath, caption):
    """Send photo as file upload"""
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendPhoto"
    try:
        with open(filepath, 'rb') as photo:
            files = {'photo': photo}
            data = {
                'chat_id': chat_id,
                'caption': caption[:1024],
                'parse_mode': 'HTML'
            }
            resp = requests.post(url, files=files, data=data, timeout=30)
            result = resp.json()
            if result.get("ok"):
                return True
            else:
                print(f"  Upload error: {result.get('description', 'unknown')}")
                return False
    except Exception as e:
        print(f"  Upload exception: {e}")
        return False
```

### Filtering Out Emoji Images

Emoji images from `telegram.org/img/emoji/` should not be sent as post images:

```python
# Skip emoji images
if 'telegram.org/img/emoji' not in url_candidate:
    image_url = url_candidate
```

## Pitfalls

1. **Bot must be channel admin** - Can't send without admin rights
2. **HTML parsing breaks** - Use flexible regex
3. **Duplicate sends** - Track sent IDs; clear when changing filters
4. **Rate limits** - Add delays or get 429 errors
5. **Image-only posts** - Filter out posts with no text
6. **CDN image URLs may fail** - Some Telegram CDN URLs are not accessible via Bot API sendPhoto. Always fallback to text-only.
7. **Caption length limit** - Telegram captions max 1024 characters. Truncate if needed.
