# Persian AI-Powered Spell-Check Userbot

Complete pattern for a Telethon userbot that auto-corrects outgoing messages.

## Architecture

```
User types message → Local fixes (fast) → AI fixes (complex) → Edit message
```

## Key Features

### 1. Preserve Intentional Elongations
Users sometimes write "سلامممم" or "سلاااام" for emphasis. Detect and preserve:

```python
def has_elongation(word):
    """Detect 3+ repeated characters"""
    for i in range(len(word) - 2):
        if word[i] == word[i+1] == word[i+2]:
            return True
    return False

def get_base_form(word):
    """Remove repeated chars to get base form for dictionary lookup"""
    if not word:
        return word
    base = word[0]
    for i in range(1, len(word)):
        if word[i] != word[i-1]:
            base += word[i]
    return base
```

**CRITICAL**: Elongated words should still have their base form checked against the dictionary. If `خيليييي` is typed, the base form `خيلي` should be looked up and corrected to `خیلی`, then one extra char is added to preserve the elongation feel: `خیلیی`.

```python
# In local_fix(), handle elongated words:
if has_elongation(word):
    base = get_base_form(word)
    # Check if base form is in dictionary
    if base in LOCAL_FIXES:
        corrected_base = LOCAL_FIXES[base]
        # Keep one extra char to preserve elongation feel
        if len(word) > len(base):
            fixed_words.append(corrected_base + corrected_base[-1])
        else:
            fixed_words.append(corrected_base)
        continue
    # Also check Arabic variants of base
    base_k = base.replace('ک', 'ك')
    base_y = base.replace('ی', 'ي')
    if base_k in LOCAL_FIXES:
        corrected_base = LOCAL_FIXES[base_k]
        if len(word) > len(base):
            fixed_words.append(corrected_base + corrected_base[-1])
        else:
            fixed_words.append(corrected_base)
        continue
    # Keep elongated word as-is if no fix found
    fixed_words.append(word)
    continue
```

### 2. Preserve Protected Words (Swear Words, Informal)
Maintain a list of words that should NEVER be changed:

```python
PROTECTED_WORDS = [
    "کص", "کصکش", "کیر", "کیری", "کون", "کونی",
    "ننه", "جنده", "حروم", "حرومی",
    "خفه", "گمشو",
    "عینی", "خفن", "سیکتیر",
]

def is_protected(word):
    word_lower = word.lower().strip('؟!.,؛')
    for protected in PROTECTED_WORDS:
        if protected in word_lower or word_lower in protected:
            return True
    return False
```

### 3. Two-Tier Correction Pipeline

**CRITICAL: AI must run FIRST, then local fixes.** The AI is smarter and catches errors the local dictionary misses (e.g., "قمگین" → "غمگین"). If local fixes run first, the AI sees already-partially-fixed text and may miss errors.

```python
def fix_text(text):
    # Step 1: AI fixes FIRST (smarter, catches complex errors)
    ai_fixed = ai_fix(text)
    if ai_fixed and ai_fixed != text:
        return ai_fixed, True
    
    # Step 2: Fast local fixes (dictionary fallback)
    fixed = local_fix(text)
    if fixed != text:
        return fixed, True
    
    return text, False
```

**Why this order matters:**
- AI sees the ORIGINAL text with all errors → can fix "قمگین" → "غمگین"
- If local runs first, AI sees "قمگین" still (not in local dict) but may not catch it
- Local dictionary is the fallback for when AI is rate-limited or fails

### 4. OpenRouter AI Integration

```python
def ai_fix(text):
    prompt = f"""تو یک ویرایشگر متن فارسی هستی. متن زیر را بررسی کن و تمام غلط‌های املایی و نگارشی را اصلاح کن.

قوانین مهم:
1. اگر کلمه‌ای کشیده شده (مثلاً سلامممم) آن را تغییر نده
2. هیچ کلمه‌ای را حذف یا اضافه نکن
3. فقط غلط‌های املایی را درست کن
4. نیم‌فاصله‌ها را درست کن
5. تغییرات معنایی نده

متن ورودی:
{text}

متن اصلاح شده:"""

    response = requests.post(
        "https://openrouter.ai/api/v1/chat/completions",
        headers={"Authorization": f"Bearer {API_KEY}"},
        json={
            "model": "google/gemma-4-26b-a4b-it:free",
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": 500,
            "temperature": 0.1
        },
        timeout=15
    )
    
    if response.status_code == 200:
        fixed = response.json()["choices"][0]["message"]["content"].strip()
        fixed = preserve_elongations(text, fixed)
        return fixed
    return None
```

## Event Handler

```python
@client.on(events.NewMessage(outgoing=True))
async def handler(event):
    text = event.message.text
    if not text or len(text) < 2:
        return
    
    fixed_text, was_fixed = fix_text(text)
    
    if was_fixed and fixed_text != text:
        await asyncio.sleep(0.5)  # Rate limit
        try:
            await event.message.edit(fixed_text)
        except Exception as e:
            print(f"Edit failed: {e}")
```

## Private Messages Only

To skip groups and channels, check `event.is_private`:

```python
@client.on(events.NewMessage(outgoing=True))
async def handler(event):
    # Only check private messages (not groups or channels)
    if not event.is_private:
        return
    
    text = event.message.text
    # ... rest of handler
```

## AI Prompt Best Practices

The AI prompt must be explicit to avoid incorrect changes:

```python
prompt = f"""تو یک ویرایشگر متن فارسی هستی. متن زیر را بررسی کن و فقط غلط‌های املایی را اصلاح کن.

قوانین مهم:
1. اگر کلمه‌ای کشیده شده (مثل سلامممم) آن را تغییر نده
2. هیچ کلمه‌ای را حذف یا اضافه نکن
3. فقط غلط‌های املایی را درست کن
4. نیم‌فاصله‌ها را درست کن
5. کلمات عامیانه مثل خوبی، ممنون، باشه را تغییر نده
6. اگر متن درست است، همان متن را برگردان

متن ورودی:
{text}

متن اصلاح شده:"""
```

## Pitfalls

1. **AI sometimes changes protected words**: The prompt must explicitly say "هیچ کلمه‌ای را حذف یا اضافه نکن"
2. **AI makes incorrect changes**: Words like "پیشی" may be changed to "متن" incorrectly. Add explicit instructions: "اگر متن درست است، همان متن را برگردان"
3. **OpenRouter 429 rate limits**: Free models frequently return 429. All free models share the same rate pool — switching models doesn't help. Disable AI for 5 minutes on 429 and fall back to local fixes only. See `references/openrouter-free-models.md` for the pattern.
4. **Rate limiting**: Add `asyncio.sleep(0.5)` before editing to avoid Telegram rate limits
5. **Duplicate edits**: Track edited message IDs to avoid re-editing
6. **AI response includes extra text**: Strip quotes and whitespace from AI response
7. **AI MUST run before local fixes**: If local fixes run first, AI sees partially-fixed text and misses errors like "قمگین" → "غمگین". The AI is smarter — let it see the original text.
8. **Only check private messages**: Use `if not event.is_private: return` to skip groups/channels
9. **Use JSON dictionary, not hardcoded dict**: For 80K+ word dictionaries, load from a JSON file instead of hardcoding in the script. See `references/persian-typo-dictionary.md` for the generation pipeline from `hicte/moin` (32K words), `b00f/lilak` lexicon (85K words), and `b00f/lilak` dic_users (13K words) GitHub repos. Pattern: `with open("persian_dict.json") as f: LOCAL_FIXES = json.load(f)` then `LOCAL_FIXES.update(EXTRA_FIXES)` for hand-crafted additions. With all three sources plus character substitutions, expect 126K+ entries (~5MB JSON). For maximum coverage, use additional sources (hazm 180K, shekar 78K, poetry 73K) and generate letter swap variants to reach 1.3M+ entries (~38MB, loads in 0.9s).
10. **Hardcode API keys when env vars fail**: If `os.environ.get("OPENROUTER_API_KEY")` returns None (environment not configured), hardcode the key directly in the script. Environment variables in cron/agent sessions may not be inherited.
11. **SQLITE session errors**: Session files can become locked (`database is locked`) or readonly (`attempt to write a readonly database`). Fix: `chmod 666 *.session*` and delete stale files with `rm -f *.session*` before restarting.
12. **Session file must have auth key**: After deleting session files, the bot will ask for authentication code + 2FA password. Use PTY mode (`pty=true`) for interactive auth, or use file-based IPC pattern.
13. **ALWAYS test API keys before deploying**: Before hardcoding an API key in a script, test it with a simple curl/requests call. We hit 401 "User not found" because the wrong key was hardcoded. Test pattern: `curl -H "Authorization: Bearer $KEY" https://openrouter.ai/api/v1/models` — should return 200.
14. **Multiple API keys for different services**: Different bots/services may use different OpenRouter API keys. Don't assume the key from one script works in another. Check each script's actual key value.
15. **OpenRouter daily rate limits**: Free models share a daily limit (50 requests/day without credits, 1000 with $10 credits). When rate-limited (429), the error includes `X-RateLimit-Reset` (Unix ms timestamp) in metadata. Calculate remaining wait: `reset_ms = error["metadata"]["headers"]["X-RateLimit-Reset"]; remaining_hours = (reset_ms/1000 - time.time()) / 3600`. The daily cap resets at midnight UTC, NOT after 5 minutes. ALL free models share the same rate pool — switching models does NOT help. Either wait until midnight UTC or add $10 credits. Disable AI for the calculated duration and fall back to local fixes only.
16. **USER PREFERENCE: Test before telling user to test**: When fixing a bug, test the fix YOURSELF first. Don't tell the user "go test it" — verify it works, THEN tell the user. The user said "بیین درستش کن و خودت تست و کن هر وقت کار کرد بگو اوکی برو تست کن کصخل" (fix it and test it yourself, only tell me when it works).
17. **Dictionary must cover ALL typo categories**: A comprehensive dictionary needs: (a) ك→ک character fixes, (b) ی→ي character fixes, (c) combined ك+ي fixes for words with both characters, (d) half-space (نیم‌فاصله) fixes for compound verbs, (e) compound word spacing fixes (چهخبر→چه خبر), (f) common misspellings (قمگین→غمگین), (g) slang/colloquial fixes (مچكرم→ممنونم), (h) additional Arabic→Persian character substitutions (ة→ه, ؤ→و, etc.). Missing any category leaves gaps users will hit.
18. **Test ALL categories before deploying**: Run tests covering each typo category: character swaps, half-spaces, compound words, misspellings, slang. Example: `('چهخبر', 'چه خبر')` tests compound words, `('ميشه كمكم كني', 'می‌شه کمکم کنی لطفاً')` tests half-spaces, `('كد كرد كنه كني', 'کد کرد کنه کنی')` tests combined ك+ي fixes, `('موبايل', 'موبایل')` tests additional character substitutions.
19. **Dictionary iteration order matters for half-space fixes**: If `ميره` maps to `میره` (ي→ی) but `میره` should map to `می‌ره` (with half-space), the first mapping wins. Fix by overriding: `d['میره'] = 'می‌ره'` to force the correct chain. More specific fixes (half-space versions) must be added AFTER basic ك→ک/ی→ي conversions.
20. **CRITICAL: Dictionary size causes OOM kills**: Background processes on this VPS have a ~953MB cgroup memory limit. A 1.3M entry dictionary (~38MB JSON) causes exit code 137 (SIGKILL) during loading. **MAXIMUM SAFE SIZE: ~400K entries (~16MB JSON)**. If you need more coverage, prioritize quality over quantity — keep the most common/important entries and remove low-value long phrases. Score entries by: short words (≤3 chars) = highest priority, ك→ک/ي→ي conversions = high priority, half-space fixes = medium priority, long phrases = lower priority.
21. **Elongated words must have base form corrected**: Old behavior: skip elongated words entirely. New behavior: extract base form via get_base_form() (remove consecutive repeated chars), check dictionary, correct base, keep one extra char for elongation feel. If base form not in dictionary, keep word as-is (e.g., سلامممم stays as سلامممم because سلام is already correct).
22. **Memory-efficient batch processing for large dictionaries**: When processing 1M+ dictionary entries for variant generation, iterating over all keys at once causes OOM kills (exit code 137). Process in batches of 100K keys and save intermediate results after each major step.
23. **Letter confusion pairs for comprehensive coverage**: Add these character confusion pairs to catch phonetic/visual typos: ث↔س (ثالث/سوم), ت↔ط (تخت/طخت), ذ↔ز (ذره/زره), ظ↔ض (ظرف/ضرب), غ↔ق (قورت/غورت), ح↔ه (حرف/هرف), چ↔ج (چی/جی), ژ↔ز (ژله/زله), ف↔پ (فنجان/پنجان), ک↔گ (کیک/گیگ). These cover common Persian typos where users confuse similar-sounding or similar-looking letters.
24. **Remove same-key-value entries**: After all processing, filter out entries where `k == v` (pointless corrections). Also remove single-character entries (len(k) == 1) as they're rarely useful and waste space.
### 25. **User demands comprehensive coverage**: Users get frustrated when specific typos aren't caught. Always test with real user examples before deploying. If user reports a typo like "خثتم" not being fixed, check if the specific letter confusion (ث→س) is covered in the dictionary.

### 26. **Session strings for cloud deployment (Railway, Render, etc.)**: For Telethon userbots deployed to cloud platforms, use **session strings** instead of `.session` files. Generate locally with `gen_session_string.py` and set as `SESSION_STRING` environment variable.

```python
# gen_session_string.py
from telethon.sync import TelegramClient
API_ID = 31844510
API_HASH = "b1722fa9a615a9cdf394ee3886765b97"
PHONE = "+19432518923"
with TelegramClient('session_gen', API_ID, API_HASH) as client:
    client.start(phone=PHONE)
    string = client.session.save()
    print(string)
```

In the bot code, use `StringSession`:
```python
from telethon import TelegramClient, StringSession
SESSION_STRING = os.environ.get("SESSION_STRING", "")
client = StringSession(SESSION_STRING)
await client.connect()
```

**Benefits**: No file locking issues, works in ephemeral containers, no `.session` file to manage.

### 27. **Maximum safe dictionary size**: VPS cgroup memory limit (~953MB) causes OOM kills (exit code 137) when loading large dictionaries. **MAXIMUM SAFE SIZE: ~400K entries (~16MB JSON)**. A 1.3M entry dictionary (~38MB JSON) consistently crashes. Prioritize quality over quantity:
- Score entries: short words (≤3 chars) = highest priority
- ك→ک/ي→ي conversions = high priority  
- Half-space fixes = medium priority
- Long phrases = lower priority

### 28. **Comprehensive typo coverage requires letter confusion pairs**: Add these phonetic/visual confusion pairs to catch common Persian typos:
- ث↔س (ثالث/سوم)
- ت↔ط (تخت/طخت)
- ذ↔ز (ذره/زره)
- ظ↔ض (ظرف/ضرب)
- غ↔ق (قورت/غورت)
- ح↔ه (حرف/هرف)
- چ↔ج (چی/جی)
- ژ↔ز (ژله/زله)
- ف↔پ (فنجان/پنجان)
- ک↔گ (کیک/گیگ)

### 29. **Dictionary iteration order for half-space fixes**: If `ميره` → `میره` (ي→ی) but `میره` should map to `می‌ره` (half-space), the first mapping wins. Fix by overriding specific entries AFTER basic conversions: `d['میره'] = 'می‌ره'`. More specific fixes must be added after basic character conversions.

### 30. **Elongated word base-form correction**: New behavior (not skip):
1. Extract base form via `get_base_form()` (remove consecutive repeated chars)
2. Check dictionary for base form
3. Correct base, keep one extra char for elongation feel
4. If base not in dictionary, keep word as-is (e.g., سلامممم stays سلامممم)

### 31. **Memory-efficient batch processing for large dictionaries**: When processing 1M+ entries for variant generation, iterating all keys at once causes OOM. Process in batches of 100K and save intermediate results after each major step.

### 32. **USER PREFERENCE: Test ALL typo categories before deploying**: Run tests covering each category: character swaps, half-spaces, compound words, misspellings, slang. Example: `('چهخبر', 'چه خبر')` tests compounds, `('ميشه كمكم كني', 'می‌شه کمکم کنی لطفاً')` tests half-spaces, `('كد كرد كنه كني', 'کد کرد کنه کنی')` tests combined ك+ي fixes, `('موبايل', 'موبایل')` tests additional character substitutions.

### 33. **USER PREFERENCE: Test fixes yourself before telling user to test**: Verify fixes work locally, THEN tell user to test. The user explicitly said: "fix it and test it yourself, only tell me when it works."

## Bale App Compatibility

The Bale messaging app (Iranian) has a Bot API similar to Telegram's:

### Bale Bot API
- **Base URL**: `https://tapi.bale.ai/bot<token>/METHOD_NAME`
- **Get bot info**: `https://tapi.bale.ai/bot<TOKEN>/getMe`
- **Send message**: `https://tapi.bale.ai/bot<TOKEN>/sendMessage`
- **Edit message**: `https://tapi.bale.ai/bot<TOKEN>/editMessageText`

### Key Differences from Telegram
1. Base URL is `https://tapi.bale.ai` not `https://api.telegram.org`
2. Bot tokens are obtained from @BotFather in Bale (not Telegram)
3. aiogram may not work directly with Bale - use requests library instead
4. API structure is very similar to Telegram Bot API

### Using requests instead of aiogram

```python
BOT_TOKEN = "your_bale_token"
BALE_API_URL = f"https://tapi.bale.ai/bot{BOT_TOKEN}"

def send_message(chat_id, text):
    url = f"{BALE_API_URL}/sendMessage"
    payload = {"chat_id": chat_id, "text": text}
    resp = requests.post(url, json=payload, timeout=10)
    return resp.json().get("ok", False)

def edit_message(chat_id, message_id, text):
    url = f"{BALE_API_URL}/editMessageText"
    payload = {"chat_id": chat_id, "message_id": message_id, "text": text}
    resp = requests.post(url, json=payload, timeout=10)
    return resp.json().get("ok", False)
```

### Polling for updates

```python
def get_updates(offset=None):
    url = f"{BALE_API_URL}/getUpdates"
    params = {}
    if offset:
        params["offset"] = offset
    resp = requests.get(url, params=params, timeout=30)
    return resp.json()
```

### Critical Limitation: Bot API Cannot Edit User Messages

**Bots cannot edit messages sent by users.** Only userbots (Telethon, using a real user account) can edit messages. This is a Telegram/Bale API restriction, not a library issue.

**Workaround for Bot API bots**: Send a new message with the correction instead of trying to edit:

```python
# ❌ This FAILS for Bot API bots:
await bot.edit_message_text(chat_id, msg_id, fixed_text)

# ✅ This WORKS: Send correction as new message
reply = f"✏️ اصلاح شد:\n\n{text}\n\n✅ {fixed_text}"
send_message(chat_id, reply)
```

**When to use which:**
- **Telethon userbot** (real user account): Can edit own messages → use `event.message.edit()`
- **Bot API bot** (bot token): Cannot edit user messages → send new message with correction

### Important Notes
- Bale Bot API does NOT support aiogram's `base_url` parameter reliably
- Use raw requests library for Bale bot development
- The spell-check logic (local fixes + AI) works the same as Telegram
- Only monitor private messages: `if message.get("chat", {}).get("type") != "private": continue`
