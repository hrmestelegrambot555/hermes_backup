# Persian Dictionary Management Patterns

From the spellcheck userbot session: building a 1.1M-entry Persian typo correction dictionary with multiple sources and typo variant generation.

## Source Datasets Used

| Source | Repo | Words | Contribution |
|--------|------|-------|--------------|
| Moin | `hicte/moin` | 32,618 | Persian dictionary, Arabic→Persian char variants |
| Lilak | `b00f/lilak` | 93,889 | Modern Persian lexicon |
| Lilak Users | `b00f/lilak` (dic_users) | 13,221 | User-added words |
| Hazm | `roshan-research/hazm` | 180,057 | Comprehensive Persian word list |
| Shekar | `amirivojdan/shekar` | 78,520 | Vocabulary from textbooks |
| Persian Poetry | `amnghd/Persian_poems_corpus` | 73,693 | Classical/poetic vocabulary |
| ParsinLU | `persiannlp/parsinlu` | 6,110 | QQP dataset pairs |

**Total unique source words:** ~478,000

## Typo Variant Generation

Generated 1.1M corrections from ~478K base words:

```python
# 1. Character variants (Arabic → Persian)
variants = {
    'ك': 'ک',  # Arabic kaf → Persian kaf
    'ي': 'ی',  # Arabic ye → Persian ye
    'ء': '',   # Hamza removal
    'ؤ': 'و',  # Hamza on waw
    'ئ': 'ی',  # Hamza on ye
}

# 2. Half-space fixes (common Persian spacing errors)
half_space_fixes = {
    'میخوام': 'می‌خوام', 'میشه': 'می‌شه', 'کنی': 'کنی',
    'خواهشمیکنم': 'خواهش می‌کنم', 'ثبتنام': 'ثبت نام',
    'موبایل': 'موبایل', 'اینترنت': 'اینترنت',
}

# 3. Combined ک+ی variants
for word in base_words:
    yield word.replace('ک', 'ك').replace('ی', 'ي')  # Arabic form
    yield word.replace('ک', 'گ').replace('ی', 'ی')  # etc.

# 4. Compound words (no space)
compounds = ['چهخبر', 'خواهشمیکنم', 'ثبتنام', 'موبایل', 'اینترنت']

# 5. Mega typo generation (keyboard proximity, deletion, insertion, substitution)
def generate_typos(word):
    # Keyboard neighbors (Persian layout)
    neighbors = {'پ': 'چ', 'چ': 'پ', 'ج': 'چ', 'س': 'ص', 'ص': 'س', ...}
    # Single char deletion
    # Single char insertion  
    # Single char substitution
    # Transposition
    # Elongation preservation (سلامممم → سلام)
```

## Memory-Efficient Loading

```python
# Option 1: JSON (simple, but loads all into RAM)
with open("persian_dict.json") as f:
    LOCAL_FIXES = json.load(f)  # 1.1M entries → ~500MB RAM

# Option 2: SQLite with WAL (disk-based, ~50MB RAM)
import sqlite3
conn = sqlite3.connect("dictionary.db")
conn.execute("PRAGMA journal_mode=WAL")
conn.execute("CREATE TABLE IF NOT EXISTS dict (wrong TEXT PRIMARY KEY, correct TEXT)")
conn.executemany("INSERT OR IGNORE INTO dict VALUES (?, ?)", fixes.items())

def local_fix(text):
    words = text.split()
    return " ".join(conn.execute("SELECT correct FROM dict WHERE wrong=?", (w,)).fetchone()[0] if conn.execute("SELECT correct FROM dict WHERE wrong=?", (w,)).fetchone() else w for w in words.split())

# Option 3: Compressed pickle (faster load, smaller memory)
import gzip, pickle
with gzip.open("persian_dict.pkl.gz", "wb") as f:
    pickle.dump(LOCAL_FIXES, f)
# Load: pickle.load(gzip.open("persian_dict.pkl.gz"))
```

## Elongation & Protected Words

```python
PROTECTED_WORDS = ["کص", "کیر", "کون", "فاک", "شیت", "dick", "fuck", "shit"]

def has_elongation(word):
    return any(word[i] == word[i+1] == word[i+2] for i in range(len(word)-2))

def get_base_form(word):
    if not word: return word
    base = word[0]
    for i in range(1, len(word)):
        if word[i] != word[i-1]:
            base += word[i]
    return base

def is_protected(word):
    return any(p in word.lower() for p in PROTECTED_WORDS)

def local_fix(text):
    words = text.split()
    fixed = []
    for word in words:
        if is_protected(word):
            fixed.append(word)
            continue
        if word in LOCAL_FIXES:
            fixed.append(LOCAL_FIXES[word])
            continue
        if has_elongation(word):
            base = get_base_form(word)
            if base in LOCAL_FIXES:
                corrected = LOCAL_FIXES[base]
                if len(word) > len(base):
                    fixed.append(corrected + corrected[-1])
                else:
                    fixed.append(corrected)
                continue
        fixed.append(word)
    return " ".join(fixed)
```

## Full Correction Pipeline

```python
async def correct_text(text):
    # 1. Try AI first (context-aware, handles complex cases)
    if OPENROUTER_API_KEY:
        ai_result = await ai_fix(text)
        if ai_result and ai_result != text:
            return ai_result, "ai"
    
    # 2. Local dictionary (fast, preserves elongations/swear words)
    local_result = local_fix(text)
    if local_result != text:
        return local_result, "local"
    
    return text, "none"
```

## File Sizes

| Format | Size | Load Time | RAM Usage |
|--------|------|-----------|-----------|
| JSON | 44 MB | 0.9s | ~500 MB |
| SQLite (WAL) | 48 MB | 0.1s | ~50 MB |
| Gzipped pickle | 12 MB | 0.3s | ~300 MB |

**Recommendation:** SQLite for 1M+ entries, JSON for <500K, gzipped pickle for fastest load with moderate RAM.