# Resolving GitHub Push Protection (Secret Scanning)

## The Problem

GitHub's secret scanning blocks pushes that contain detected secrets (API keys, tokens, passwords, etc.) in **any commit in the push**, including historical commits.

## Quick Fix (Already Pushed)

```bash
# 1. Remove file from ALL history
git filter-branch --force --index-filter \
  'git rm --cached --ignore-unmatch PATH_TO_SENSITIVE_FILE' \
  --prune-empty --tag-name-filter cat -- --all

# 2. Force push cleaned history
git push origin BRANCH --force

# 3. Verify
git log --all --full-history -- PATH_TO_SENSITIVE_FILE
# Should show no results
```

## Prevention

1. **Use allowlist + denylist** in backup script (see `templates/backup-script.sh`)
2. **Run denylist cleanup AFTER copy** — ensures files never enter commit
3. **Add `.gitignore`** for sensitive patterns:
   ```
   *.key
   *.pem
   .env
   auth.json
   state.db
   *.cache.json
   cache/
   logs/
   ```
4. **Pre-commit hook** (optional):
   ```bash
   # .git/hooks/pre-commit
   git diff --cached --name-only | xargs grep -l "SECRET_PATTERN" && exit 1
   ```

## If You Can't Rewrite History

- Go to GitHub repo → Security → Secret scanning → "Allow this secret" (for false positives)
- Rotate the exposed secret immediately
- Use a deploy key instead of PAT for automated pushes

## Tools

- `git filter-repo` — faster, safer alternative to filter-branch (install via pip)
- `truffleHog` / `git-secrets` — local pre-push scanning