# Persian Typo Patterns for Auto-Correction

## Common Persian Letter Swaps

### ص/س (Sad/Sin) confusion
| Typo | Correct |
|------|---------|
| صلام | سلام |
| ثلام | سلام |
| سلامم | سلام |
| سلاممم | سلام |
| صبح | صبح (correct) |
| صبر | صبر (correct) |

### ب/پ (Be/Pe) confusion
| Typo | Correct |
|------|---------|
| خبی | خوبی |
| خوبم | خوبم |

### ت/ط (Te/Ta) confusion
| Typo | Correct |
|------|---------|
| چتوری | چطوری |
| چجوری | چطوری |

### Preposition merging (می + verb)
The most common Persian writing mistake: forgetting the ZWNJ (zero-width non-joiner) in compound verbs.

| Typo | Correct |
|------|---------|
| میخوام | می‌خوام |
| میخوای | می‌خوای |
| میخواد | می‌خواد |
| میشه | می‌شه |
| میکنه | می‌کنه |
| میکنم | می‌کنم |
| میتونم | می‌تونم |
| میتونه | می‌تونه |
| میبرم | می‌برم |
| میارم | می‌ارم |
| میرم | می‌رم |
| مینویسم | می‌نویسم |
| میخواستم | می‌خواستم |
| خواهش میکنم | خواهش می‌کنم |
| عذر میخوام | عذر می‌خوام |

### Negation prefix (نمی + verb)
| Typo | Correct |
|------|---------|
| نمیخوام | نمی‌خوام |
| نمیشه | نمی‌شه |
| نمیکنه | نمی‌کنه |
| نمیتونم | نمی‌تونم |
| نمیرم | نمی‌رم |

## Implementation Pattern

```python
PERSIAN_COMPOUND_VERBS = {
    "میخوام": "می‌خوام",
    "میخوای": "می‌خوای",
    "میخواد": "می‌خواد",
    "میشه": "می‌شه",
    "میکنه": "می‌کنه",
    "میکنم": "می‌کنم",
    "میتونم": "می‌تونم",
    "میتونه": "می‌تونه",
    "نمیخوام": "نمی‌خوام",
    "نمیشه": "نمی‌شه",
    "خواهش میکنم": "خواهش می‌کنم",
}

def fix_persian_typos(text):
    fixed = text
    for wrong, correct in PERSIAN_COMPOUND_VERBS.items():
        fixed = fixed.replace(wrong, correct)
    return fixed
```

## AI-Powered Correction

For errors beyond simple pattern matching, use an LLM API:

```python
import requests

def ai_fix_persian(text, api_key):
    prompt = f"""تو یک ویرایشگر متن فارسی هستی. متن زیر را بررسی کن و فقط غلط‌های املایی و نگارشی را اصلاح کن.
تغییرات معنایی نده. فقط غلط‌ها را درست کن.
اگر متن بدون غلط بود، همان متن اصلی را برگردان.

متن ورودی:
{text}

متن اصلاح شده:"""

    response = requests.post(
        "https://openrouter.ai/api/v1/chat/completions",
        headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
        json={"model": "google/gemma-4-26b-a4b-it:free", "messages": [{"role": "user", "content": prompt}], "max_tokens": 500, "temperature": 0.1},
        timeout=10
    )
    return response.json()["choices"][0]["message"]["content"].strip()
```

## Building a 80K+ Word Dictionary

### Source 1: moin (32K words)

The `hicte/moin` repo has 32,618 Persian words already in correct form (with proper ک and ی):

```bash
curl -sL "https://raw.githubusercontent.com/hicte/moin/main/all.txt" -o /tmp/moin_words.txt
```

### Source 2: Lilak Lexicon (85K+ words) — RECOMMENDED

The `b00f/lilak` repo has a much larger lexicon (93,889 lines, 85,837 unique words). This is the best source for building a comprehensive dictionary:

```bash
curl -sL "https://raw.githubusercontent.com/b00f/lilak/master/src/data/lexicon" -o /tmp/lilak_lexicon.txt
```

**Format**: CSV with header `### word,pos,offensive,ends_with_vowel,ends_with_aah_uh`. Parse with:
```python
words = set()
with open("/tmp/lilak_lexicon.txt", "r", encoding="utf-8") as f:
    for line in f:
        if line.startswith("##") or line.startswith("###") or not line.strip():
            continue
        word = line.strip().split(",")[0].strip()
        if word and len(word) > 1:
            words.add(word)
```

### Source 3: Lilak dic_users (13K words)

The `b00f/lilak` repo also has a user-contributed word list:

```bash
curl -sL "https://raw.githubusercontent.com/b00f/lilak/master/src/data/dic_users" -o /tmp/lilak_dic_users.txt
```

**Format**: One word per line, already in correct Persian. Process same as Lilak lexicon.

### Generation Pipeline

**KEY INSIGHT**: If source words already use correct Persian characters (ک/ی), generate the ARABIC variants (ك/ي) as the typo→correct mappings. This is the opposite of what you might initially think.

```python
import json

# Load existing dictionary
with open("persian_dict.json", "r", encoding="utf-8") as f:
    d = json.load(f)

# Load word list (e.g., from Lilak)
words = set()
with open("/tmp/lilak_lexicon.txt", "r", encoding="utf-8") as f:
    for line in f:
        if line.startswith("##") or line.startswith("###") or not line.strip():
            continue
        word = line.strip().split(",")[0].strip()
        if word and len(word) > 1:
            words.add(word)

# Generate ARABIC variants (the typos users actually make)
added = 0
for word in words:
    # If word has ک → create entry: ك version → correct version
    if "ک" in word:
        typo = word.replace("ک", "ك")
        if typo != word and typo not in d:
            d[typo] = word
            added += 1
    
    # If word has ی → create entry: ي version → correct version
    if "ی" in word:
        typo = word.replace("ی", "ي")
        if typo != word and typo not in d:
            d[typo] = word
            added += 1

# Remove pointlessly same entries
d = {k: v for k, v in d.items() if k != v and k.strip() and v.strip()}

# Result: 81,724 entries!
with open("persian_dict.json", "w", encoding="utf-8") as f:
    json.dump(d, f, ensure_ascii=False, indent=2)
```

**Why this works**: Arabic code pages (ك, ي) are the #1 source of Persian typos — keyboard layouts and old systems output these instead of proper Persian (ک, ی). This single conversion catches the majority of real-world typos.

### Loading Dictionary in Script

Load from JSON instead of hardcoding — much cleaner and easier to update:

```python
import json

with open("persian_dict.json", "r", encoding="utf-8") as f:
    LOCAL_FIXES = json.load(f)

# Add hand-crafted extras on top
EXTRA_FIXES = {
    "میخوام": "می‌خوام",  # half-space fixes
    "قمگین": "غمگین",      # common misspellings
    "مچكرم": "ممنونم",    # colloquial
}
LOCAL_FIXES.update(EXTRA_FIXES)
```

### Combined Variants (CRITICAL PITFALL)

**Single-character substitutions are NOT enough.** Words containing BOTH ک and ی need a combined variant where BOTH characters are wrong simultaneously.

Example: `کنی` has both ک and ی. Users might type:
- `کني` (only ی→ي) ← single variant catches this
- `كنی` (only ک→ك) ← single variant catches this
- `كني` (BOTH wrong) ← **MISSED by single variants!**

```python
# Generate combined variants for words with both characters
for word in words:
    has_k = "ک" in word
    has_y = "ی" in word
    
    if has_k and has_y:
        # Combined: both ک→ك AND ی→ي
        combined = word.replace("ک", "ك").replace("ی", "ي")
        if combined != word and combined not in d:
            d[combined] = word
```

**Result**: Single variants give ~81K entries. Adding combined variants pushes to ~89K+ entries.

### Additional Character Substitutions (ح→ه, etc.)

Beyond ك→ک and ی→ي, users make other character errors:

| Typo | Correct | Description |
|------|---------|-------------|
| چح | چه | ح instead of ه |
| چحخبر | چه خبر | Common greeting typo |
| صلام | سلام | ص instead of س |
| ثلام | سلام | ث instead of س |

**Key insight**: These are NOT caught by the standard ك→ک/ی→ي pipeline. Add them as separate dictionary entries.

## Character Substitution Variants (126K+ total)

Beyond ك→ک and ی→ي, there are other Arabic→Persian character substitutions:

```python
char_subs = {
    'ك': 'ک',  # Arabic kaf → Persian kaf
    'ي': 'ی',  # Arabic yeh → Persian yeh
    'ة': 'ه',  # Ta marbuta → Heh
    'ٱ': 'ا',  # Wasla → Alef
    'ؤ': 'و',  # Hamza on Waw → Waw
    'إ': 'ا',  # Alef with Hamza below → Alef
    'أ': 'ا',  # Alef with Hamza above → Alef
    'ء': 'ا',  # Hamza → Alef
    'ۀ': 'ه',  # Heh with Hamza → Heh
    'ٹ': 'ت',  # Tteh → Te
    'ڈ': 'د',  # Ddal → Dal
    'ڑ': 'ر',  # Rreh → Re
    'ں': 'ن',  # Noon ghunna → Nun
}

# Generate all variants for existing entries
for word, correct in list(d.items()):
    for wrong_char, right_char in char_subs.items():
        if wrong_char in word:
            variant = word.replace(wrong_char, right_char)
            if variant != word and variant not in d:
                d[variant] = correct
```

**Result**: Adding character substitutions pushes from ~99K to ~126K entries.

### Half-Space (نیم‌فاصله) Fixes

Persian compound verbs require ZWNJ (zero-width non-joiner) between prefix and verb. This is the #1 colloquial typo:

```python
HW_FIXES = {
    "میخوام": "می‌خوام", "میخوای": "می‌خوای", "میخواد": "می‌خواد",
    "میشه": "می‌شه", "میکنه": "می‌کنه", "میکنم": "می‌کنم",
    "میتونم": "می‌تونم", "میتونه": "می‌تونه", "میتونی": "می‌تونی",
    "میگم": "می‌گم", "میگه": "می‌گه",
    "میرم": "می‌رم", "میره": "می‌ره",
    "میدم": "می‌دم", "میده": "می‌ده",
    "میدونم": "می‌دونم", "میدونی": "می‌دونی",
    "نمیخوام": "نمی‌خوام", "نمیشه": "نمی‌شه",
    "خواهش میکنم": "خواهش می‌کنم",
}
```

**Pitfall**: These must be added AFTER the JSON dictionary load, as separate entries. The JSON only has ك→ک and ی→ي variants, NOT half-space fixes.

## Compound Word Fixes (Missing Spaces)

Persian speakers often write compound words without spaces. The dictionary should catch these:

```python
COMPOUND_FIXES = {
    "چهخبر": "چه خبر", "چخبر": "چه خبر", "چخبار": "چه خبر",
    "خواهشمیکنم": "خواهش می‌کنم", "عذرمیخوام": "عذر می‌خوام",
    "خسته‌نباشید": "خسته نباشید", "موفق‌باشید": "موفق باشید",
    "به‌سلامتی": "به سلامتی", "خوش‌بگذره": "خوش بگذره",
    "ثبتنام": "ثبت نام", "خدانگهدار": "خدانگهدار",
    # Also generate Arabic variants
    # "چهخبر" → already has no ك/ي, but compound words like
    # "خواهشمیکنم" generate: "خواهشميكنم" (both wrong)
}
```

**Key pattern**: For each compound word, also generate the Arabic ك/ي variants:
```python
for word, correct in COMPOUND_FIXES.items():
    # ك variant
    if "ک" in word:
        typo = word.replace("ک", "ك")
        if typo not in d:
            d[typo] = correct
    # ی variant
    if "ی" in word:
        typo = word.replace("ی", "ي")
        if typo not in d:
            d[typo] = correct
    # Combined variant (both wrong)
    if "ک" in word and "ی" in word:
        typo = word.replace("ک", "ك").replace("ی", "ي")
        if typo not in d:
            d[typo] = correct
```

### Pitfalls

1. **Hand-crafting 5000+ words is impractical** — use a real word list source (Lilak: 85K words)
2. **Many "unique" words produce duplicate entries** — always check `if typo not in d` before adding
3. **Source words already use correct Persian** (ک/ی, not ك/ي) — so generate the ARABIC variants as the typo→correct mappings (NOT the other way around)
4. **Removing entries where wrong == correct**: Always filter `d = {k: v for k, v in d.items() if k != v}` to avoid pointless entries
5. **Dictionary size**: With both moin + Lilak, expect 80K+ entries (~3.5MB JSON). This loads fine at startup but don't try to hardcode it in the script.
6. **Single-character variants miss combined errors**: Words with BOTH ک and ی need a third variant where both are wrong simultaneously (e.g., `کنی` → `كني`). Without this, users who type both Arabic characters won't get corrected.
7. **Half-space fixes are separate from character fixes**: The JSON dictionary handles ك→ک and ی→ي, but نیم‌فاصله fixes (میخوام→می‌خوام) must be added as separate dictionary entries.
8. **Dictionary iteration order matters**: If `ميره` maps to `میره` (ي→ی) but `میره` should map to `می‌ره` (with half-space), the first mapping wins. Fix by overriding: `d['میره'] = 'می‌ره'` to force the correct chain. More specific fixes (half-space versions) must be added AFTER basic ك→ک/ی→ي conversions.
9. **Compound words need their own entries**: Words like `چهخبر` (no space) are not caught by ك→ک or ی→ي conversions because they don't contain those characters. Add compound word fixes as separate dictionary entries.
10. **CRITICAL: Dictionary size and process stability**: Large dictionaries (1M+ entries, ~44MB JSON) CAN work on VPS with ~953MB cgroup limit, BUT background processes may get killed (exit code 137) for OTHER reasons. **ROOT CAUSE CHECK**: Before assuming OOM, check for zombie Python processes holding SQLite session locks. Scan `/proc/*/cmdline` for leftover `spellcheck_userbot.py` processes and kill them (`kill -9 PID`). The SQLite `database is locked` error causes Telethon to hang/crash, which looks like OOM but isn't. **SAFE SIZE**: 1.1M entries at 44MB JSON works reliably when no zombies exist. For maximum safety, keep ≤400K entries (~16MB). Score entries by priority: short words (≤3 chars) = highest, к→К/ی→ي conversions = high, half-space fixes = medium, long phrases = lower.
11. **Memory-efficient batch processing**: When processing 1M+ dictionary entries for variant generation, iterating over all keys at once causes OOM kills. Process in batches of 100K keys: `for i in range(0, len(keys), 100000): process(keys[i:i+100000])`. Save intermediate results after each major step.
12. **Letter confusion pairs for comprehensive coverage**: Add these character confusion pairs to catch phonetic/visual typos: ث↔س, ت↔ط, ذ↔ز, ظ↔ض, غ↔ق, ح↔ه, چ↔ج, ژ↔ز, ف↔پ, ک↔گ. For each existing entry, check if ANY char matches a confusion pair and generate the variant. This alone can add 500K+ entries (but may exceed memory limits).
13. **Additional word sources**: Beyond moin (32K) and lilak (85K+13K), these sources add significant coverage: hazm words.dat (180K), shekar vocab.csv (78K), Persian poetry corpus (73K), shekar compound_words.csv (10K), parsinlu QQP (6K). Download from: `roshan-research/hazm`, `amirivojdan/shekar`, `amnghd/Persian_poems_corpus`.
14. **Override chain for half-space fixes**: When adding half-space fixes like `میره` → `می‌ره`, you must also update the Arabic ي variant `ميره` to point directly to `می‌ره` (not to `میره`). Otherwise the dictionary iteration picks the wrong target: `ميره` → `میره` (from ي→ی conversion) instead of `میره` → `می‌ره` (the correct half-space version).
15. **Elongated words must have base form corrected**: Old behavior: skip elongated words entirely (`خيليييي` → `خيليييي`). New behavior: extract base form (`خيلي`), check dictionary, correct base, keep one extra char for elongation feel (`خيليييي` → `خیلیی`). Implemented via `get_base_form()` helper that removes consecutive repeated chars.
16. **User demands comprehensive coverage**: Users get frustrated when specific typos aren't caught. Always test with real user examples before deploying. If user reports a typo like "خثتم" not being fixed, check if the specific letter confusion (ث→س) is covered in the dictionary.
17. **Remove single-character entries**: After all processing, filter out entries where `len(k) == 1` as they're rarely useful and waste space.

### Testing the Dictionary

Always test with comprehensive before/after pairs:

```python
def test_dictionary(local_fix):
    tests = [
        ('صلام خوبی چطوری', 'سلام خوبی چطوری'),
        ('مچكرم خيلي ممنونم', 'ممنونم خیلی ممنونم'),
        ('میخوام برم خونه', 'می‌خوام برم خونه'),
        ('قمگین نباش خوشحال باش', 'غمگین نباش خوشحال باش'),
        ('سيب خيلي خوشمزه بود', 'سیب خیلی خوشمزه بود'),
        ('ميشه كمكم كني لطفا', 'می‌شه کمکم کنی لطفاً'),
        ('ميگه ميره مياد ميدم', 'می‌گه می‌ره میاد می‌دم'),
        ('چهخبر', 'چه خبر'),
        ('خواهشمیکنم', 'خواهش می‌کنم'),
        ('ثبتنام', 'ثبت نام'),
        ('كد كرد كنه كني', 'کد کرد کنه کنی'),
        ('نميره نميدم نميگم', 'نمی‌ره نمی‌دم نمی‌گم'),
    ]
    all_pass = True
    for text, expected in tests:
        fixed = local_fix(text)
        if fixed != expected:
            all_pass = False
            print(f'❌ {text} → {fixed} (expected {expected})')
    if all_pass:
        print('🎉 ALL TESTS PASSED!')
```

## Two-Tier Approach

1. **Local fixes** (fast, no API call): 80K+ word dictionary covers most common typos
2. **AI fixes** (slower, API call): Complex grammar, unusual typos, context-dependent errors

**CRITICAL ORDER: AI FIRST, then local.** The AI is smarter and catches errors the local dictionary misses (e.g., "قمگین" → "غمگین"). If local fixes run first, the AI sees already-partially-fixed text and may miss errors.

```python
def fix_text(text):
    # Step 1: AI fixes FIRST (smarter, catches complex errors)
    ai_fixed = ai_fix(text)
    if ai_fixed and ai_fixed != text:
        return ai_fixed, True
    
    # Step 2: Fast local fixes (dictionary fallback)
    local_fixed = local_fix(text)
    if local_fixed != text:
        return local_fixed, True
    
    return text, False
```

**Why this order matters:**
- AI sees the ORIGINAL text with all errors → can fix complex typos
- If local runs first, AI sees partially-fixed text and may miss errors
- Local dictionary is the fallback for when AI is rate-limited or fails

## Intentional Elongation Preservation

Users sometimes intentionally repeat characters for emphasis (e.g., `سلامممم`, `میخوووام`, `عالیییی`). These should NOT be corrected.

### Detection Pattern

```python
def has_elongation(word):
    """Check if word has intentional elongation (3+ consecutive identical chars)"""
    for i in range(len(word) - 2):
        if word[i] == word[i+1] == word[i+2]:
            return True
    return False
```

### Preservation Logic

```python
def preserve_elongations(original, fixed):
    """Keep intentional elongations from original text"""
    orig_words = original.split()
    fixed_words = fixed.split()
    result = []
    for word in orig_words:
        if has_elongation(word):
            result.append(word)  # Keep elongated words as-is
        else:
            if fixed_words:
                result.append(fixed_words.pop(0))
            else:
                result.append(word)
    return ' '.join(result)
```

### AI Prompt Addition

Include this in AI correction prompts:
```
مهم: اگر کلمه‌ای کشیده شده (مثلاً سلامممم، میخوووام، عالیییی) آن را تغییر نده.
این کشیدن‌ها عمدی هستند.
```

## Protected Words (Swear Words & Informal Language)

**CRITICAL**: Users may write swear words, slang, or informal expressions that AI should NOT "correct". The AI might replace these with random words (e.g., "کص کش" → "با توجه").

### Why This Happens

AI models are trained to be "helpful" and may interpret swear words as errors to fix. Without explicit protection:
- User writes: "کص کش"
- AI changes to: "با توجه" ❌

### Detection Pattern

```python
PROTECTED_WORDS = [
    # Swear words - preserve as-is
    "کص", "کصکش", "کیر", "کیری", "کون", "کونی",
    "ننه", "جنده", "حروم", "حرومی", "حرومزاده",
    
    # Informal/slang - preserve as-is
    "خفه", "گمشو", "سیکتیر",
    "والا", "دیگه", "چجوری",
    
    # English swear words
    "fuck", "shit", "ass", "damn",
]

def is_protected(word):
    """Check if a word should not be changed"""
    word_lower = word.lower().strip('؟!.,؛')
    for protected in PROTECTED_WORDS:
        if protected in word_lower or word_lower in protected:
            return True
    return False
```

### Combined Preservation Logic

```python
def preserve_all(original, fixed):
    """Keep elongations AND protected words from original"""
    orig_words = original.split()
    fixed_words = fixed.split()
    result = []
    for word in orig_words:
        if has_elongation(word) or is_protected(word):
            result.append(word)  # Keep as-is
        else:
            if fixed_words:
                result.append(fixed_words.pop(0))
            else:
                result.append(word)
    return ' '.join(result)
```

### AI Prompt Addition

Add this to prevent AI from changing protected content:
```
۶. هیچ کلمه‌ای را حذف یا اضافه نکن
۷. کلمات عامیانه و فحش‌ها را تغییر نده
```

## Complete Userbot Pattern

```python
def fix_text(text):
    """Complete text correction with all protections"""
    if not text or len(text) < 2:
        return text, False
    
    # Tier 1: Local fixes (respects elongations + protected)
    fixed = local_fix(text)
    
    # Tier 2: AI fixes (always run)
    ai_fixed = ai_fix(fixed if fixed != text else text)
    if ai_fixed and ai_fixed != text:
        return ai_fixed, True
    
    if fixed != text:
        return fixed, True
    
    return text, False
```
