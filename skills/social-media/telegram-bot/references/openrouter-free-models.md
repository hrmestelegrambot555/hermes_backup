# OpenRouter Free Model Discovery

How to find and use free AI models via OpenRouter API.

## List Free Models

```python
import requests

def list_free_models(api_key):
    resp = requests.get(
        "https://openrouter.ai/api/v1/models",
        headers={"Authorization": f"Bearer {api_key}"}
    )
    models = resp.json().get("data", [])
    free = [m for m in models if ":free" in m["id"]]
    
    for m in free:
        print(f"- {m['id']}: {m.get('name', 'N/A')}")
    return free
```

## Check API Key Status

```python
def check_key_status(api_key):
    resp = requests.get(
        "https://openrouter.ai/api/v1/auth/key",
        headers={"Authorization": f"Bearer {api_key}"}
    )
    data = resp.json()["data"]
    print(f"Free tier: {data['is_free_tier']}")
    print(f"Usage: ${data['usage']}")
    print(f"Expires: {data.get('expires_at', 'Never')}")
```

## Use a Free Model

```python
def ai_fix(text, api_key):
    response = requests.post(
        "https://openrouter.ai/api/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        },
        json={
            "model": "google/gemma-4-26b-a4b-it:free",
            "messages": [{"role": "user", "content": text}],
            "max_tokens": 500,
            "temperature": 0.1
        },
        timeout=15
    )
    return response.json()["choices"][0]["message"]["content"]
```

## Popular Free Models (as of 2026)

| Model | Provider | Good For |
|-------|----------|----------|
| `google/gemma-4-26b-a4b-it:free` | Google | Text editing, Persian |
| `google/gemma-4-31b-it:free` | Google | General purpose |
| `nvidia/nemotron-3-ultra-550b:free` | NVIDIA | Complex reasoning |
| `openai/gpt-oss-20b:free` | OpenAI | Code, text |

## Rate Limit Handling (429 Errors)

Free models frequently hit 429 (Too Many Requests). All free models share the same rate limit pool, so switching models doesn't help.

**Pattern: Graceful degradation with timed disable**

```python
import time

def ai_fix(text, api_key):
    # Check if rate limited
    if not hasattr(ai_fix, 'rate_limited_until'):
        ai_fix.rate_limited_until = 0
    
    if time.time() < ai_fix.rate_limited_until:
        return None  # Skip AI, use local fixes only
    
    # Minimum delay between calls
    if not hasattr(ai_fix, 'last_call'):
        ai_fix.last_call = 0
    if time.time() - ai_fix.last_call < 2:
        return None
    ai_fix.last_call = time.time()
    
    response = requests.post(...)
    
    if response.status_code == 429:
        ai_fix.rate_limited_until = time.time() + 300  # Disable for 5 min
        print("⚠️ Rate limited - AI disabled for 5 minutes")
        return None
    
    # ... normal processing
```

**Key insight**: When 429 hits, ALL free models are rate-limited simultaneously. Don't try switching models — just wait and fall back to local fixes.

## Pitfalls

1. **Rate limits**: Free models frequently return 429. On 429, disable AI for 5 minutes and use local fixes only.
2. **All free models share rate pool**: Switching from gemma to nemotron on 429 doesn't help — all return 429 simultaneously
3. **Token limits**: Free models may have lower max_tokens (500-1000)
4. **Model names change**: Check `/api/v1/models` periodically
5. **No expiration**: Free tier keys don't expire, but usage may be throttled
6. **Quality varies**: Test models for your specific use case before committing
