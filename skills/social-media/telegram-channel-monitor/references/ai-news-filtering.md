# AI-Powered News Filtering

Use OpenRouter API (free Gemma model) for intelligent news filtering instead of keyword matching.

## Pattern

```python
OPENROUTER_API_KEY = "sk-or-v1-..."
AI_MODEL = "google/gemma-4-26b-a4b-it:free"

def ai_check_importance(text):
    """Use AI to check if news is very important"""
    prompt = f"""You are a news editor for a Persian news channel.
Analyze this Persian news text and determine if it's VERY important (breaking news).

IMPORTANT CRITERIA:
- War, military attacks, explosions, casualties
- Major political events (elections, treaties, resignations)
- Natural disasters (earthquakes, floods)
- Economic crises
- International conflicts

Reply with ONLY "YES" if very important, or "NO" if not.
Be STRICT - only truly breaking news gets YES.

News: {text[:500]}"""

    response = requests.post(
        "https://openrouter.ai/api/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "Content-Type": "application/json"
        },
        json={
            "model": AI_MODEL,
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": 10
        },
        timeout=15
    )

    if response.status_code == 200:
        result = response.json()
        answer = result.get("choices", [{}])[0].get("message", {}).get("content", "").strip().upper()
        return "YES" in answer
    return False

def ai_summarize(text):
    """Use AI to create a clean summary"""
    prompt = f"""Summarize this Persian news in 1-2 sentences.
Keep it factual, remove source names and links.
Output ONLY the summary in Persian.

News: {text[:800]}"""

    response = requests.post(
        "https://openrouter.ai/api/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "Content-Type": "application/json"
        },
        json={
            "model": AI_MODEL,
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": 150
        },
        timeout=20
    )

    if response.status_code == 200:
        result = response.json()
        return result.get("choices", [{}])[0].get("message", {}).get("content", "").strip()
    return text
```

## Verifying API Key

Before using an OpenRouter API key, verify it's valid:

```bash
curl -s "https://openrouter.ai/api/v1/auth/key" -H "Authorization: Bearer YOUR_KEY"
```

Valid response shows `limit`, `usage`, and `rate_limit` fields.

Invalid key returns: `{"error":{"message":"User not found.","code":401}}`

## Complete Integration Pattern

```python
import os
import requests
import time

OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY", "")
AI_MODEL = "google/gemma-4-26b-a4b-it:free"

def ai_check_importance(text):
    """Check if news is very important using AI"""
    prompt = f"""Analyze this Persian news text and determine if it's VERY important.
Reply with ONLY "YES" if very important, or "NO" if not.

News: {text[:500]}"""
    
    try:
        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "model": AI_MODEL,
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": 10
            },
            timeout=15
        )
        
        if response.status_code == 200:
            answer = response.json()["choices"][0]["message"]["content"].strip().upper()
            return "YES" in answer
        else:
            print(f"  AI error: {response.status_code}")
            return False
    except Exception as e:
        print(f"  AI exception: {e}")
        return False

def ai_summarize(text):
    """Create clean summary using AI"""
    prompt = f"""Summarize this Persian news in 1-2 sentences.
Keep it factual, remove source names and links.
Output ONLY the summary in Persian.

News: {text[:800]}"""
    
    try:
        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "model": AI_MODEL,
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": 150
            },
            timeout=20
        )
        
        if response.status_code == 200:
            return response.json()["choices"][0]["message"]["content"].strip()
        return text
    except:
        return text

# Usage in forwarder
if ai_check_importance(post["text"]):
    summary = ai_summarize(post["text"])
    send_to_channel(summary)
    time.sleep(1)  # Rate limiting
```

## Benefits over Keyword Filtering

1. **Context-aware**: Understands Persian language nuance
2. **Flexible**: Catches important news that keywords miss
3. **Summarization**: Can clean up and summarize news
4. **Strict filtering**: Reduces noise significantly

## Pitfalls

- **API key validity**: OpenRouter keys can expire or be revoked
- **Rate limits**: Free tier has limits. Add `time.sleep(2)` every 3 API calls
- **Token cost**: Each news item costs ~100-200 tokens
- **Response parsing**: AI may return extra text. Check for "YES" in response, don't expect exact match
- **Empty API key**: If `OPENROUTER_API_KEY` is empty, AI functions silently fail. Always verify key before deployment
