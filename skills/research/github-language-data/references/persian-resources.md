# Persian Language Resources on GitHub

## Known Repos with Word Lists / Lexicons

### roshan-research/hazm (1412 ★) — Persian NLP Toolkit
- **Path:** `hazm/data/`
- **Files:** `words.dat` (193K lines), `verbs.dat` (692 lines), `iwords.dat`, `iverbs.dat`, `stopwords.dat` (389 lines), `abbreviations.dat`
- **Format (.dat):** Tab-separated `word\tpos\ttags` (UTF-8)
- **Verbs format:** `infinitive#conjugated` separated by `/` and spaces
- **Clean extraction:** 180K unique words, 1.2K verbs, 348 stopwords

### amirivojdan/shekar (73 ★) — Simplifying Persian NLP
- **Path:** `shekar/data/files/`
- **Files:** `vocab.csv` (1.5MB, 83K lines), `compound_words.csv` (207KB, 10K lines), `verbs.csv` (365 lines), `loanword_mappings.csv` (77KB, 1.7K lines), `informal_words.csv` (208 lines), `stopwords.csv` (300 lines), `offensive_words.csv`
- **Format (.csv):** CSV with `word,frequency` columns
- **Clean extraction:** 78.5K vocab words, 10.2K compounds, 1.7K loanwords, 328 verbs, 182 informal, 301 stopwords

### b00f/lilak (165 ★) — Persian Spell Checking Dictionary
- **Path:** `src/data/`
- **Files:** `lexicon` (2.7MB), `dic_users` (234KB), `affixes` (5.3KB), `verbs.htm` (55KB)
- **Format:** LibreOffice spell-check format. `lexicon` has word+POS. `affixes` is hunspell-style affix rules. `verbs.htm` is HTML with verb conjugations.
- **Note:** Original `dic_full` and `dic_official` paths DO NOT EXIST (404).

### mahdevar/Dictionaries (1 ★) — Hunspell Farsi
- **Files:** `fa_IR.dic` (527 words), `fa_IR.aff`
- **Format:** Hunspell `.dic` — line 1 is count, rest are `word/affix_flags`
- **Very small** — only 527 base words with affix expansion

### amnghd/Persian_poems_corpus (81 ★) — Persian Poetry
- **Path:** `normalized/` (47 poet files, largest: attar 9.3MB, ferdousi 4.5MB, bidel 3.9MB)
- **Format:** Plain text, one verse per line
- **Extract:** Regex tokenization yields 73K+ unique words from 6 largest poets

### persiannlp/parsinlu (169 ★) — Persian NLU Suite
- **Path:** `data/qqp/` (train.jsonl, test.jsonl, dev.jsonl)
- **Format:** JSONL with `q1`, `q2`, `label` fields
- **Extract:** ~6K unique words from QQP question pairs

## Common Data Formats

| Format | Source | Structure | Extraction |
|--------|--------|-----------|------------|
| `.dat` tab-sep | hazm | `word\tpos\ttags` | `line.split('\t')[0]` |
| `.csv` | shekar | `word,frequency` | `csv.reader`, `row[0]` |
| `.dic` hunspell | mahdevar | `word/flags` per line | `line.split('/')[0]`, skip line 1 |
| `.html` verb lists | lilak | HTML tables | Regex extract Persian tokens |
| `.jsonl` NLP tasks | parsinlu | `{"q1": "...", "q2": "..."}` | `json.loads`, regex on text fields |
| plain text corpus | poems | One verse per line | Regex tokenization |

## Persian/Arabic Unicode Ranges

```python
PERSIAN_REGEX = r'[\u0600-\u06FF\u0750-\u077F\u08A0-\u08FF\uFB50-\uFDFF\uFE70-\uFEFF]+'
# Covers: Arabic, Arabic Supplement, Arabic Extended-A, Arabic Presentation Forms-A, Arabic Presentation Forms-B
```

## URLs That Failed (404)

- `raw.githubusercontent.com/b00f/lilak/master/src/data/dic_full` — does not exist
- `raw.githubusercontent.com/b00f/lilak/master/src/data/dic_official` — does not exist
- `raw.githubusercontent.com/wordlist/wordlist/main/persian.txt` — does not exist
- `raw.githubusercontent.com/hooshvaf/FarsTail/master/data/words.txt` — does not exist
- LINDAT FaSpell download (`lindat.mff.cuni.cz/.../allzip`) — not a valid zip

## Search Query Patterns That Worked

```
# Repository search
?q=persian+wordlist+OR+farsi+dictionary+OR+persian+nlp
?q=%D8%B2%D8%A8%D8%A8%D8%A7%D9%86+%D9%81%D8%A7%D8%B1%D8%B3%DB%8C (native script)
?q=persian+hunspell+OR+fa+hunspell
?q=%D9%84%DA%AF%D8%AA+OR+persian+lexicon+OR+persian+spellcheck

# Code search
?q=persian+words+extension:txt+filename:words
?q=farsi+words+extension:txt+in:path
```
