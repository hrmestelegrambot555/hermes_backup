---
name: github-language-data
description: Find and extract linguistic data from GitHub repos.
---

# GitHub Language Resource Collection

Workflow for discovering and extracting linguistic data (word lists, lexicons, corpora, stop words, verb conjugations) from GitHub repositories via the GitHub API.

## When to Use

- User asks to download word lists, lexicons, or linguistic data for a specific language
- User wants to build a corpus or vocabulary from open-source NLP repos
- User provides specific GitHub URLs that may or may not exist (always verify)

## Workflow

### Phase 1: Download Known URLs (fast-fail)

When the user provides specific URLs, try them first but **expect 404s**. Many GitHub raw URLs in tutorials and blog posts go stale.

```bash
curl -sL "URL" -o /tmp/output.txt
# Check size — <100 bytes usually means 404
wc -l /tmp/output.txt
```

**Pitfall:** Do NOT assume success just because curl exited 0. Always verify file size and content. A 14-byte file saying "404: Not Found" is the most common failure mode.

### Phase 2: GitHub API Search

When direct URLs fail, search the GitHub API:

```bash
# Search by language/topic keywords
curl -s "https://api.github.com/search/repositories?q=persian+wordlist+OR+farsi+dictionary&sort=stars&per_page=15"

# Search for code files matching a pattern
curl -s "https://api.github.com/search/code?q=persian+words+extension:txt+in:path&per_page=10"
```

**Tips:**
- Use OR between keyword variants (English + native script)
- Sort by stars for quality signal
- Check repo `contents` endpoint to explore structure before downloading

### Phase 3: Explore Repo Structure

Before downloading large files, explore the repo tree:

```bash
curl -s "https://api.github.com/repos/OWNER/REPO/contents/"
curl -s "https://api.github.com/repos/OWNER/REPO/contents/path/to/dir"
```

Look for directories named: `data/`, `files/`, `datasets/`, `resources/`, `statics/`.

### Phase 4: Download and Extract

Download raw data files, then extract clean word lists.

**Tab-separated .dat format** (hazm style):
```python
words = set()
for line in open('file.dat', encoding='utf-8'):
    parts = line.strip().split('\t')
    if parts: words.add(parts[0])
```

**CSV format** (shekar style):
```python
import csv
words = set()
for row in csv.reader(open('file.csv', encoding='utf-8')):
    if row: words.add(row[0].strip())
```

**Hunspell .dic format**:
```python
for i, line in enumerate(open('fa_IR.dic', encoding='utf-8')):
    if i == 0: continue
    word = line.strip().split('/')[0]
```

**Verb conjugation files** (`infinitive#conjugated` with `/` separators):
```python
parts = line.split('#')
for part in parts:
    subparts = re.split(r'[/\s]+', part)
```

**JSONL format** (NLP task data):
```python
import json
data = json.loads(line)
for key in ['q1', 'q2', 'text']:
    tokens = re.findall(PERSIAN_REGEX, data.get(key, ''))
```

### Phase 5: Unicode Filtering

Extract only target-script characters from mixed-format files:

```python
import re
PERSIAN_REGEX = r'[\u0600-\u06FF\u0750-\u077F\u08A0-\u08FF\uFB50-\uFDFF\uFE70-\uFEFF]+'
words = {w for w in extracted if re.match(r'^[\u0600-\u06FF\u0750-\u077F\u08A0-\u08FF\uFB50-\uFDFF\uFE70-\uFEFF]+$', w)}
```

## Output Best Practices

1. Save cleaned word lists as one-word-per-line `.txt` files in `/tmp/`
2. Use descriptive names: `{source}_{content}_clean.txt`
3. Save raw/original files separately with original extensions
4. Report word counts for each file
5. Create a summary table at the end

## Common Failure Modes

| Problem | Solution |
|---------|----------|
| curl returns 200 but file is "404: Not Found" | Check file size; <100 bytes = error page |
| Unicode shows as garbled text | File is UTF-8; process with Python, not shell |
| GitHub API returns empty results | Try different keyword combos, include native script |
| Large files timeout | Use `--max-time 30` and download in background |
| Zip files from research repos corrupted | Often multi-part archives; skip and try alternatives |
