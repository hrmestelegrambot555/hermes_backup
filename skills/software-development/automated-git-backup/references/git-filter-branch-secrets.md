# Git Filter-Branch for Secret Removal

## Problem

GitHub Push Protection (secret scanning) rejects pushes containing secrets, tokens, or large files — even if they're in **history**, not the current commit.

Common blocked items:
- `state.db` — SQLite databases often contain auth tokens
- `.env` files — API keys, tokens
- `auth.json` — OAuth credentials
- Large cache files (>100MB)

## Solution: git filter-branch

Removes a file from **entire git history** (all commits, all branches):

```bash
# Remove single file from all history
git filter-branch --force --index-filter \
  'git rm --cached --ignore-unmatch path/to/file' \
  --prune-empty --tag-name-filter cat -- --all

# Remove multiple files
git filter-branch --force --index-filter \
  'git rm --cached --ignore-unmatch file1 file2 dir/' \
  --prune-empty --tag-name-filter cat -- --all
```

## Flags Explained

| Flag | Purpose |
|------|---------|
| `--force` | Overwrite existing backup refs |
| `--index-filter` | Fast: operates on index only (no checkout) |
| `git rm --cached --ignore-unmatch` | Remove from index; don't fail if missing |
| `--prune-empty` | Drop commits that become empty |
| `--tag-name-filter cat` | Rewrite tags too |
| `-- --all` | Apply to all refs (branches + tags) |

## After Filter-Branch

```bash
# Force push cleaned history
git push origin <branch> --force

# Clean up local refs
git for-each-ref --format='delete %(refname)' refs/original | git update-ref --stdin
git reflog expire --expire=now --all
git gc --prune=now --aggressive
```

## Verification

```bash
# Confirm file is gone from ALL history
git log --all --full-history -- path/to/file
# Should return nothing

# Confirm file not in any commit
git rev-list --all | xargs -r git ls-tree -r | grep path/to/file
# Should return nothing
```

## Alternative: BFG Repo-Cleaner (faster for large repos)

```bash
# Download
wget https://repo1.maven.org/maven2/com/madgag/bfg/1.14.0/bfg-1.14.0.jar

# Remove file
java -jar bfg-1.14.0.jar --delete-files state.db

# Or remove large files
java -jar bfg-1.14.0.jar --strip-blobs-bigger-than 100M

# Clean up
git reflog expire --expire=now --all && git gc --prune=now --aggressive
git push origin --force --all
```

## Prevention: Pre-commit Hook

Add to `.git/hooks/pre-commit`:

```bash
#!/bin/bash
# Block commits with sensitive patterns
patterns=("state.db" "auth.json" ".env" "*.key" "*.pem" "ghp_" "sk-")
for pattern in "${patterns[@]}"; do
    if git diff --cached --name-only | grep -qE "$pattern"; then
        echo "BLOCKED: $pattern detected in staged files"
        exit 1
    fi
done
```

## Hermes Backup Context

In our backup script, these items are **explicitly excluded** from backup (denylist):
- `state.db` — contains tokens, session data
- `auth.json` — OAuth credentials
- `*.cache.json` — large cache files
- `.env` — secrets
- `audio_cache/`, `image_cache/`, `cache/`, `logs/`, `sandboxes/` — temporary/large

If they slip through, use filter-branch above to purge from history.