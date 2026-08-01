---
name: persian-nlp-dictionary
description: "Build Persian spell-check dicts from corpora with typos."
version: 1.0.0
tags: [persian, nlp, dictionary, spellcheck, corpus]
---

# Persian NLP Dictionary Builder

Build production-ready Persian dictionaries (1M+ entries) from open-source corpora with automatic typo variant generation for spell-checking systems.

## Scope & Trigger

**Use when:** Building spell-check dictionaries for Persian/Farsi, need typo variant generation, combining multiple corpora, or creating lookup tables for text correction.

**Class of task:** Persian NLP data pipeline — corpus acquisition → cleaning → normalization → variant generation → deduplication → export.

## Pipeline Stages

### 1. Corpus Acquisition
```bash
# Moin Dictionary (32K words)
wget -O moin.txt https://raw.githubusercontent.com/hicte/moin/master/moin.txt

# Lilak Lexicon (93K words)
wget -O lilak.txt https://raw.githubusercontent.com/b00f/lilak/main/lexicon.txt

# Hazm words.dat (180K words) - needs parsing
wget -O hazm_words.dat https://github.com/roshan-research/hazm/raw/master/hazm/data/words.dat

# Shekar vocab (78K words)
wget -O shekar.csv https://raw.githubusercontent.com/amirivojdan/shekar/main/vocab.csv

# Persian Poetry Corpus (73K words)
wget -O poetry.txt https://raw.githubusercontent.com/amnghd/Persian_poems_corpus/main/poems.txt
```

### 2. Normalization Rules
Apply **before** variant generation:
```python
# Arabic → Persian character mapping
ARABIC_TO_PERSIAN = {
    'ك': 'ک',  # KAF
    'ي': 'ی',  # YEH
    'ٔ': '',   # HAMZA (remove)
    'ۀ': 'ه',  # HEH with yeh
}

# Half-space normalization
HALF_SPACE_FIXES = {
    'میخوام': 'می‌خوام',
    'میشه': 'می‌شه',
    'کنی': 'کنی',
    'نمیشه': 'نمی‌شه',
}
```

### 3. Typo Variant Generation
Generate **systematic variants** for each base word:
```python
def generate_variants(word):
    variants = {word}
    
    # Character substitutions (Arabic→Persian)
    variants.add(word.replace('ک', 'ك'))
    variants.add(word.replace('ی', 'ي'))
    variants.add(word.replace('ک', 'ك').replace('ی', 'ي'))
    
    # Half-space omission
    variants.add(word.replace('‌', ''))
    variants.add(word.replace(' ', ''))
    
    return variants
```

### 4. Memory-Efficient Processing
**Critical for 1M+ entries:**
```python
# Use batch processing with generators
def process_in_batches(words, batch_size=10000):
    for i in range(0, len(words), batch_size):
        batch = words[i:i+batch_size]
        yield process_batch(batch)

# Write incrementally to avoid OOM
with open('persian_dict.json', 'w') as f:
    f.write('{')
    first = True
    for batch in process_in_batches(all_words):
        for k, v in batch.items():
            if not first:
                f.write(',')
            f.write(f'"{k}":"{v}"')
            first = False
    f.write('}')
```

## Source Corpora Reference

| Corpus | Words | Source | License |
|--------|-------|--------|---------|
| Moin | 32,618 | hicte/moin | MIT |
| Lilak Lexicon | 93,889 | b00f/lilak | MIT |
| Lilak Dic Users | 13,221 | b00f/lilak | MIT |
| Hazm | 180,057 | roshan-research/hazm | MIT |
| Shekar | 78,520 | amirivojdan/shekar | MIT |
| Persian Poetry | 73,693 | amnghd/Persian_poems | MIT |
| Parsinlu QQP | 6,110 | persiannlp/parsinlu | MIT |
| **Total Unique (after dedup)** | **~475K base** | | |

## Output Format
```json
{
  "خستم": "خسته‌ام",
  "خثتم": "خسته‌ام",
  "كمكم": "کم‌کم",
  "ميشه": "می‌شه",
  "میخوام": "می‌خوام",
  "ثبتنام": "ثبت نام"
}
```

## Pitfalls & Fixes

| Issue | Fix |
|-------|-----|
| OOM on 1.3M entries (38MB JSON) | Batch write incrementally; limit to 400K-1M entries |
| SQLite lock "database is locked" | Kill zombie processes: `pkill -f script_name` |
| Encoding corruption in form data | Decode: `text.encode('latin1').decode('utf-8')` |
| Jinja2 cache "unhashable type: dict" | Disable cache: `templates.env.cache = {}` or use string replacement |
| Elongation preservation (سلامممم) | Detect 3+ repeated chars, lookup base form, preserve last char |

## Verification
```python
# Test critical entries
test_words = ['خستم', 'خثتم', 'ميشه', 'میخوام', 'ثبتنام', 'موبايل', 'اینترنت']
for w in test_words:
    assert w in DICT, f"Missing: {w}"
```

## Performance Targets
- Load time: <1 second for 400K entries
- Memory: <200MB for 1M entries
- Lookup: O(1) dict access
- File size: ~16MB for 400K, ~44MB for 1.1M