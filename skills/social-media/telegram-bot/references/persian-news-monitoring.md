# Persian News Channel Monitoring

## Source Channels Used
- `@takhte_khabar` — اخبار ایران آمریکا | تخت خبر (327K subscribers)
- `@irannewsff` — ایران نیوز / Iran News (7.9K subscribers)

## Target Channel
- `@VelorianNet` — forwarding destination

## Bot Token
- Username: `@hermes_railway123bot`
- Token stored in session (use env var in production)

## News Filtering Approaches

### Method 1: Keyword-based (Simple)
```python
IMPORTANT_KEYWORDS = ["‼️", "🚨", "فوری:", "BREAKING", "حمله موشکی", "بمباران", "انفجار"]
def is_important(text):
    return any(kw.lower() in text.lower() for kw in IMPORTANT_KEYWORDS)
```

### Method 2: AI-powered (Recommended)
Use OpenRouter free models (Gemma 4) for intelligent filtering:

```python
OPENROUTER_API_KEY = "sk-or-v1-..."
AI_MODEL = "google/gemma-4-26b-a4b-it:free"

def ai_check_importance(text):
    prompt = f"""Analyze this Persian news. Reply ONLY "YES" if very important (war, disasters, major politics), or "NO".
News: {text[:500]}"""
    
    response = requests.post(
        "https://openrouter.ai/api/v1/chat/completions",
        headers={"Authorization": f"Bearer {OPENROUTER_API_KEY}"},
        json={"model": AI_MODEL, "messages": [{"role": "user", "content": prompt}], "max_tokens": 10},
        timeout=15
    )
    return "YES" in response.json()["choices"][0]["message"]["content"].upper()

def ai_summarize(text):
    prompt = f"""Summarize this Persian news in 1-2 sentences. Remove source names and links.
News: {text[:800]}"""
    # ... same API call pattern, max_tokens=150
```

**Key learnings**:
- Rate limit: add `time.sleep(2)` every 3 API calls
- AI makes stricter/better filtering than keyword matching
- Always include fallback: if AI fails, skip the news (don't forward everything)
- Free tier models share rate limit pool — 429 errors affect all free models for ~5 min

## Images from CDN

Images from `cdn4.telesco.pe` can't be sent directly via Bot API:
1. Download with `requests.get()` using `Referer: https://t.me/` header
2. Send as photo via `sendPhoto` with caption
3. Filter out emoji-only images (small files, telegram.org/img/emoji/ URLs)

```python
# Filter emoji images
if 'telegram.org/img/emoji' in url:
    continue  # skip
if file_size < 5000:  # likely emoji
    continue
```

## Scraping Notes
- Web preview at `https://t.me/s/channelname` returns last ~20 messages
- Paginate with `?before=MESSAGE_ID` for older messages
- HTML entities: Persian text may have encoded characters
- Posts have `data-post="channel/ID"` attribute for tracking
- Image URLs in `background-image:url()` CSS property
