# AI-Powered Telegram News Forwarder

Complete pattern for monitoring Persian Telegram channels and forwarding only VERY important news using AI filtering, with image download/upload support.

## Architecture

```
Channel (takhte_khabar, irannewsff) 
    → Fetch via t.me/s/ (web scraping)
    → Extract posts (HTML regex)
    → AI Importance Check (OpenRouter Gemma 4)
    → If VERY IMPORTANT → AI Summarize
    → Download images (cdn4.telesco.pe)
    → Send as photo with caption OR text-only
    → Track sent IDs (deduplication)
```

## Key Components

### 1. Fetching Channel Posts

```python
def fetch_channel_posts(channel_username):
    url = f"https://t.me/s/{channel_username}"
    resp = requests.get(url, timeout=15)
    html = resp.text
    
    # Extract post IDs
    post_ids = re.findall(r'data-post="([^"]+)"', html)
    
    for post_id in post_ids:
        # Extract text
        text_pattern = rf'data-post="{re.escape(post_id)}".*?js-message_text[^>]*>(.*?)</div>'
        text_match = re.search(text_pattern, html, re.DOTALL)
        
        # Extract image URL (not emoji images)
        photo_pattern = rf'data-post="{re.escape(post_id)}".*?tgme_widget_message_photo[^>]*background-image:url\([\'"]?([^\'")\s]+)[\'"]?\)'
        photo_match = re.search(photo_pattern, html, re.DOTALL)
```

### 2. AI Importance Filtering (OpenRouter)

```python
def ai_check_importance(text):
    prompt = f"""Analyze this Persian news and determine if VERY IMPORTANT.
Criteria: War, attacks, explosions, major political events, natural disasters, economic crises.
Reply ONLY "YES" or "NO". Be STRICT.

News: {text[:500]}"""

    response = requests.post(
        "https://openrouter.ai/api/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "Content-Type": "application/json"
        },
        json={
            "model": "google/gemma-4-26b-a4b-it:free",
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": 10
        },
        timeout=15
    )
    answer = response.json()["choices"][0]["message"]["content"].strip().upper()
    return "YES" in answer
```

### 3. AI Summarization

```python
def ai_summarize(text):
    prompt = f"""Summarize this Persian news in 1-2 sentences.
Keep it factual, remove source names and links.
Output ONLY the summary in Persian.

News: {text[:800]}"""
    
    # Similar API call with max_tokens=150
    return summary if summary else text
```

### 4. Image Handling (cdn4.telesco.pe)

```python
def download_image(url, post_id):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Referer': 'https://t.me/',
    }
    resp = requests.get(url, headers=headers, timeout=30)
    # Save to temp file, return path
    
# Filter: ignore telegram.org/img/emoji/ URLs (emoji-only "images")
```

### 5. Sending with Bot API

```python
def send_photo_file(chat_id, filepath, caption):
    with open(filepath, 'rb') as photo:
        files = {'photo': photo}
        data = {'chat_id': chat_id, 'caption': caption[:1024], 'parse_mode': 'HTML'}
        requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/sendPhoto", 
                      files=files, data=data)
```

### 6. Deduplication

```python
SENT_FILE = "/root/.hermes/scripts/sent_news.json"

def load_sent():
    try:
        with open(SENT_FILE) as f: return json.load(f)
    except: return {"sent_ids": []}

def save_sent(data):
    with open(SENT_FILE, 'w') as f: json.dump(data, f)

# Keep only last 500 IDs
sent_data["sent_ids"] = list(sent_ids)[-500:]
```

## Cron Job Setup

```bash
# Every 30 minutes via Hermes cron (no_agent=True)
cronjob(action='create', name='News Forwarder', 
        schedule='every 30m', 
        script='news_forwarder.py', 
        no_agent=True)
```

**Script must be in `/data/.hermes/scripts/` not `/root/.hermes/scripts/`**

```bash
cp /root/.hermes/scripts/news_forwarder.py /data/.hermes/scripts/
```

## Environment Variables

| Variable | Description |
|---|---|
| `TELEGRAM_BOT_TOKEN` | Bot token for sending (e.g., `8880783689:...`) |
| `OPENROUTER_API_KEY` | OpenRouter key for AI (e.g., `sk-or-...`) |

## Railway Deployment

For 24/7 deployment, create GitHub repo with:
- `main.py` — main script (use env vars for secrets)
- `requirements.txt` — dependencies
- `railway.json` — deployment config

**CRITICAL**: GitHub push protection blocks commits with detected secrets. Use `os.environ.get()` for tokens, never hardcode. If secret was accidentally committed, create **fresh repo** — amending doesn't fix history because Git preserves the secret in old commits.

**Bot token validation**: Always test tokens before deployment:
```bash
curl -s "https://api.telegram.org/bot{TOKEN}/getMe" | jq .ok
# Must return true
```

## Rate Limits & Cost Control

- AI calls: ~3-5 per run (filtered by importance)
- OpenRouter free tier: 10 requests/10 seconds
- Add `time.sleep(2)` after every 3 AI calls
- Skip AI if rate limited (401/429) — use local keyword fallback

## Fallback: Local Keyword Filter

```python
VERY_IMPORTANT_KEYWORDS = [
    "‼️", "🚨", "فوری:", "BREAKING",
    "حمله موشکی", "بمباران", "انفجار", "جنگ مستقیم",
    "نیروی هوایی", "سوخت‌رسان", "جنگنده",
    "توافق", "پیمان", "آتش‌بس",
    "آتش‌سوزی بزرگ", "سیل ویرانگر", "زلزله شدید",
]

def local_check(text):
    return any(kw in text.lower() for kw in VERY_IMPORTANT_KEYWORDS)
```

## Common Pitfalls

1. **Bot token unauthorized** → Token expired or bot deleted. Get new token from @BotFather.
2. **401 on image upload** → Download failed or Bot API issue. Retry with text-only fallback.
3. **Rate limited** → OpenRouter 429 error. Add exponential backoff or skip AI for this cycle.
4. **Duplicate posts** → Use sent_ids tracking with JSON file persistence.
5. **Emoji images** → Filter out `telegram.org/img/emoji/` URLs — they're not real images.
6. **Cron script path** → Must be in `/data/.hermes/scripts/`, use `no_agent=True`.
7. **GitHub push protection** → Secrets in any commit block the entire push. Use fresh repo.
8. **localtunnel security gate** → Users must enter server IP (e.g. `152.55.176.2`) on first visit.

## Complete Example

See `/root/.hermes/scripts/telegram_news_forwarder.py` for full working implementation with:
- Multi-channel support (`takhte_khabar`, `irannewsff`)
- AI importance check + summarization
- Image download/upload with emoji filtering
- Deduplication with JSON state file
- Rate limiting and error handling
- Structured logging