# AI-Powered Text Correction via OpenRouter

## Overview

Use OpenRouter's free-tier models for text correction in userbots. This enables catching errors beyond simple dictionary matching.

## Setup

### 1. Get OpenRouter API Key
- Sign up at https://openrouter.ai (free tier available)
- Create API key in dashboard

### 2. Environment Variable
```bash
export OPENROUTER_API_KEY="sk-or-v1-..."
```

### 3. Free Models Available (verified 2026-07-26)
- `google/gemma-4-26b-a4b-it:free` - Good for text correction (recommended)
- `google/gemma-4-31b-it:free` - Alternative
- `nvidia/nemotron-3-ultra-550b-a55b:free` - Larger model, very capable
- `nvidia/nemotron-3-super-120b-a12b:free` - Good balance
- `openai/gpt-oss-20b:free` - OpenAI's free offering

**NOT free:** `xiaomi/mimo-v2.5` and `xiaomi/mimo-v2.5-pro` are paid models.

**Pitfall:** Model names change. Verify available models with `GET /api/v1/models`.

## Implementation

### Basic Correction Function

```python
import requests

def ai_correct_text(text, api_key, language="fa"):
    """Use AI to correct text errors"""
    lang_instruction = {
        "fa": "تو یک ویرایشگر متن فارسی هستی",
        "en": "You are an English text editor"
    }.get(language, "You are a text editor")

    prompt = f"""{lang_instruction}. Check the text below and fix ONLY spelling and grammar errors.
Do not change meaning. Only fix errors.
If the text has no errors, return the original text.

Input text:
{text}

Corrected text:"""

    try:
        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            },
            json={
                "model": "google/gemma-4-26b-a4b-it:free",
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": 500,
                "temperature": 0.1
            },
            timeout=10
        )

        if response.status_code == 200:
            result = response.json()
            fixed = result["choices"][0]["message"]["content"].strip()
            return fixed.strip('"\'')
    except Exception as e:
        print(f"AI Error: {e}")

    return None
```

### Two-Tier Pattern (Local + AI)

```python
def fix_text(text):
    """Fix text using local dictionary first, then AI for complex cases"""
    # Tier 1: Fast local fixes
    fixed = local_dictionary_fix(text)
    if fixed != text:
        return fixed, "local"

    # Tier 2: AI for complex/unknown errors
    ai_fixed = ai_correct_text(text, API_KEY)
    if ai_fixed and ai_fixed != text:
        return ai_fixed, "ai"

    return text, None
```

## Pitfalls

1. **Rate limits**: Free tier has rate limits. Add delays between API calls.
2. **Response parsing**: AI may wrap response in quotes — strip them.
3. **Cost**: Free tier is limited. For high-volume use, consider paid tier.
4. **Latency**: AI calls add 1-3 seconds. Use local fixes for common patterns.
5. **Over-correction**: AI might change meaning. Use low temperature (0.1) and explicit instructions.
6. **Profanity filtering**: Some AI models automatically censor swear words. Add explicit instructions in prompt: "Do not change or censor any words, including profanity or informal expressions."
7. **Protected words**: Maintain a list of words that should NEVER be changed (swear words, intentional slang, elongated words like سلامممم). Check against this list before and after AI correction.

## Userbot Integration

```python
@client.on(events.NewMessage(outgoing=True))
async def handler(event):
    text = event.message.text
    if not text:
        return

    fixed_text, source = fix_text(text)

    if fixed_text != text:
        await asyncio.sleep(0.5)
        await event.message.edit(fixed_text)
        print(f"✅ [{source}] '{text[:30]}' -> '{fixed_text[:30]}'")
```
