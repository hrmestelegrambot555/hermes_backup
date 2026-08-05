---
name: automated-git-backup
description: Automate git backups with cron and secret exclusion.
category: software-development
tags: [backup, cron, git, github, automation, security]
---

# Automated Git Backup

Class-level skill for creating reliable, automated backup pipelines that push to a Git remote (GitHub, GitLab, etc.) on a schedule.

## When to Use

- Need periodic backups of config, databases, or state files to a Git repo
- Want to exclude sensitive files (secrets, tokens, large caches) automatically
- Dealing with GitHub push protection / secret scanning blocks
- Setting up cron jobs for unattended backup runs

## Core Workflow

### 1. Write Backup Script (`scripts/backup.sh`)

Key patterns:
- **Explicit allowlist** of items to backup (not denylist)
- **Separate denylist** for sensitive items that must never commit
- Use `python3 -c 'import sys,json; print(json.dumps(...))'` instead of `jq` for portability
- Atomic copy: `rm -rf "$dst" && cp -r "$src" "$dst"`
- Clean excluded items from repo after copy

```bash
BACKUP_ITEMS=(
    "config.yaml"
    "memories/"
    "skills/"
    # ... explicit allowlist
)

EXCLUDE_ITEMS=(
    "state.db"          # contains tokens
    "auth.json"         # credentials
    "*.cache.json"      # large caches
    ".env"              # secrets
    # ... denylist
)
```

### 2. Handle GitHub Push Protection

If secret scanning blocks push:
1. **Remove from history** (if already committed):
   ```bash
   git filter-branch --force --index-filter \
     'git rm --cached --ignore-unmatch sensitive_file' \
     --prune-empty --tag-name-filter cat -- --all
   ```
2. **Force push** cleaned history: `git push origin master --force`
3. **Verify** excluded items stay out of future commits

### 3. Set Up Cron Job

Use Hermes `cronjob` tool or system cron:
```bash
# Every 6 hours at minute 0
0 */6 * * * /path/to/backup.sh
```

In Hermes (agent mode - runs prompt each tick):
```python
cronjob(
    action="create",
    name="Auto Backup",
    schedule="0 */6 * * *",
    script="/path/to/backup.sh"
)
```

In Hermes (no-agent mode - runs script directly, no LLM call, no auth needed):
```python
cronjob(
    action="create",
    name="Auto Backup",
    schedule="0 */6 * * *",
    script="backup.sh",  # Relative to ~/.hermes/scripts/
    no_agent=True
)
```
**Use `no_agent: true` for pure script execution** (backups, watchdogs, health checks). The script's stdout is delivered verbatim. Requires script in `~/.hermes/scripts/`.

## Pitfalls & Fixes

| Problem | Fix |
|---------|-----|
| `jq` not installed | Use Python one-liner for JSON |
| Push rejected: secret in history | `git filter-branch` + force push |
| Wrong branch name (main vs master) | Check `git branch -a` on remote |
| Sensitive file re-added | Denylist removal runs AFTER copy in script |
| Large files (>100MB) | Add to denylist or use Git LFS |

## Security Rules

- **Never commit**: `.env`, `auth.json`, `*.key`, `*.pem`, `state.db`, cache directories
- **Rotate tokens** if accidentally pushed
- **Use PAT with minimal scope** (repo only, no admin)
- **Store PAT in script** only for unattended CI; prefer deploy keys

## Verification

After setup, run manually once:
```bash
./backup.sh
# Check repo: git log --oneline -1
# Verify excluded: ls repo/sensitive_file 2>/dev/null && echo "LEAKED" || echo "OK"
```

## References

- `references/github-push-protection.md` — resolving secret scanning blocks
- `references/cron-schedule-examples.md` — common schedules
- `references/no-agent-cron.md` — Hermes no_agent cron mode (script-only, no LLM)
- `references/git-filter-branch-secrets.md` — purge secrets from git history
- `references/hermes-version-updates.md` — Hermes Agent update workflows
- `templates/backup-script.sh` — starter script with allowlist/denylist pattern