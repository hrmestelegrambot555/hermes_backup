# OpenRouter Rate Limit Handling

Free models on OpenRouter frequently hit 429 (Too Many Requests) errors.

## Key Insight

**All free models share the same rate limit pool.** Switching from `gemma-4-26b` to `nemotron-3-ultra` on 429 does NOT help — they ALL return 429 simultaneously.

## Two Types of Rate Limits

### 1. Per-Request Throttle (short-term)
- Triggered by sending too many requests too fast
- Resets after ~5 minutes
- Error: `Rate limit exceeded: requests-per-minute`
- **Fix**: Disable AI for 5 minutes on 429

### 2. Daily Free Tier Cap (long-term)
- Triggered by exceeding daily free model usage
- Resets at **midnight UTC** (not 5 minutes)
- Error: `Rate limit exceeded: free-models-per-day. Add 10 credits to unlock 1000 free model requests per day`
- **Fix**: Wait until midnight UTC, or add $10 credits to unlock 1000 requests/day
- **Check reset time**: `metadata.headers.X-RateLimit-Reset` (Unix timestamp in milliseconds)

```python
import time, datetime

# Parse reset time from error response
reset_ms = error_response["metadata"]["headers"]["X-RateLimit-Reset"]
reset_time = datetime.datetime.fromtimestamp(reset_ms / 1000)
remaining = reset_time - datetime.datetime.now()
print(f"Rate limit resets in: {remaining}")
```

## Pattern: Graceful Degradation

```python
import time

def ai_fix(text, api_key):
    # Check if rate limited
    if not hasattr(ai_fix, 'rate_limited_until'):
        ai_fix.rate_limited_until = 0
    
    if time.time() < ai_fix.rate_limited_until:
        return None  # Skip AI, use local fixes only
    
    # Minimum delay between calls (2 seconds)
    if not hasattr(ai_fix, 'last_call'):
        ai_fix.last_call = 0
    if time.time() - ai_fix.last_call < 2:
        return None
    ai_fix.last_call = time.time()
    
    # Make API call
    response = requests.post(
        "https://openrouter.ai/api/v1/chat/completions",
        headers={"Authorization": f"Bearer {api_key}"},
        json={
            "model": "google/gemma-4-26b-a4b-it:free",
            "messages": [{"role": "user", "content": text}],
            "max_tokens": 500,
            "temperature": 0.1
        },
        timeout=15
    )
    
    if response.status_code == 429:
        error = response.json()
        metadata = error.get("error", {}).get("metadata", {})
        headers = metadata.get("headers", {})
        limit_source = metadata.get("limit_source", "")
        
        if "daily" in limit_source:
            # Daily cap — disable until midnight UTC
            reset_ms = int(headers.get("X-RateLimit-Reset", 0))
            if reset_ms:
                ai_fix.rate_limited_until = reset_ms / 1000
            else:
                ai_fix.rate_limited_until = time.time() + 3600  # 1 hour fallback
            print("⚠️ Daily limit hit — AI disabled until midnight UTC")
        else:
            # Short-term throttle — disable for 5 minutes
            ai_fix.rate_limited_until = time.time() + 300
            print("⚠️ Rate limited — AI disabled for 5 minutes")
        return None
    
    # ... normal processing
```

## Two-Tier Fallback

Always have local fixes as primary, AI as fallback:

```python
def fix_text(text):
    # Step 1: Fast local fixes (dictionary)
    local_fixed = local_fix(text)
    
    # Step 2: AI fixes (complex errors) — may be disabled
    ai_fixed = ai_fix(local_fixed)
    
    # Return best result
    if ai_fixed and ai_fixed != text:
        return ai_fixed, True
    if local_fixed != text:
        return local_fixed, True
    return text, False
```

## Checking Rate Limit Status

```python
def check_key_status(api_key):
    resp = requests.get(
        "https://openrouter.ai/api/v1/auth/key",
        headers={"Authorization": f"Bearer {api_key}"}
    )
    data = resp.json()["data"]
    print(f"Free tier: {data['is_free_tier']}")
    print(f"Usage: ${data['usage']}")
    print(f"Rate limit: {data.get('rate_limit', {})}")
```

## Pitfalls

1. **429 means ALL free models are rate-limited** — don't try switching models
2. **Two different 429 types**: short-term (5 min) vs daily (until midnight UTC)
3. **Check `limit_source`** in error metadata to distinguish them: `openrouter_free_tier_daily` = daily cap
4. **Minimum 2-second delay** between API calls to avoid triggering 429
5. **Free tier has lower max_tokens** (500-1000) compared to paid models
6. **Quality varies** — test models for your specific use case before committing
7. **API key validation**: Check `GET /api/v1/auth/key` — if `is_free_tier: true` and `usage: 0`, key is valid but rate-limited
