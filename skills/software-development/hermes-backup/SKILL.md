---
name: hermes-backup
description: "Backup and restore Hermes data to remote storage."
version: 1.0.0
author: hermes-agent
license: MIT
platforms: [linux, macos]
prerequisites:
  commands: [git, curl]
metadata:
  hermes:
    tags: [backup, github, hermes, cron, restore]
---

# Hermes Backup to Remote Storage

Use this skill for:
- Backing up Hermes data (memories, skills, config, databases)
- Pushing backups to GitHub repos
- Scheduling automated backups via cron
- Restoring from backups

## What to Backup

### Critical (always backup)
- `memories/` — User profiles, preferences, memory entries
- `skills/` — Custom and installed skills
- `cron/` — Scheduled job configurations
- `kanban.db` — Task/kanban database
- `config.yaml` — Main Hermes configuration
- `SOUL.md` — Agent personality definition

### Important (should backup)
- `state/` — System state files
- `hooks/` — Custom hooks
- `channel_directory.json` — Channel routing config
- `gateway_state.json` — Gateway status

### NEVER Backup (contains secrets)
- `state.db` — Contains session data with tokens
- `auth.json` — Contains authentication credentials
- `.env` — Contains environment secrets
- `.git/` — Git history (redundant with remote)

## Backup Script Template

```bash
#!/bin/bash
set -e

HERMES_DIR="$HOME/.hermes"
BACKUP_DIR="/tmp/hermes_backup_$(date +%Y%m%d_%H%M%S)"
REPO_URL="https://${TOKEN}@github.com/user/repo.git"
TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')

echo "🔄 Starting backup at $TIMESTAMP"

mkdir -p "$BACKUP_DIR"

# Copy critical data (skip missing dirs gracefully)
for item in memories skills cron hooks state; do
    [ -d "$HERMES_DIR/$item" ] && cp -r "$HERMES_DIR/$item" "$BACKUP_DIR/"
done

for item in kanban.db config.yaml SOUL.md channel_directory.json gateway_state.json; do
    [ -f "$HERMES_DIR/$item" ] && cp "$HERMES_DIR/$item" "$BACKUP_DIR/"
done

# Create metadata
cat > "$BACKUP_DIR/backup_info.json" << EOF
{
  "timestamp": "$TIMESTAMP",
  "hostname": "$(hostname)"
}
EOF

# Push to GitHub
cd "$BACKUP_DIR"
git init
git config user.email "backup@hermes.bot"
git config user.name "Hermes Backup"
git remote add origin "$REPO_URL" 2>/dev/null || git remote set-url origin "$REPO_URL"
git add -A
git commit -m "backup: $TIMESTAMP" || echo "Nothing new"
git push --force origin main 2>&1 || git push --force origin master 2>&1

echo "✅ Backup completed"
rm -rf "$BACKUP_DIR"
```

## GitHub Integration

### HTTPS with Token (when SSH port 22 is blocked)

```bash
REPO_URL="https://${TOKEN}@github.com/user/repo.git"
git remote add origin "$REPO_URL"
```

### Push Protection Pitfall

GitHub's push protection scans for secrets in commits. Files like `state.db` may contain tokens that trigger blocking.

**Error**: `push declined due to repository rule violations — Push cannot contain secrets`

**Solutions**:
1. Never backup `state.db`, `auth.json`, `.env`
2. If a file is large and may contain secrets, skip it
3. Use `.gitignore` in backup repo if needed
4. **⚠️ Memory files can contain secrets:** `memories/MEMORY.md` and `memories/USER.md` often contain API keys (OpenRouter `sk-or-...`, GitHub `ghp_...`), phone numbers, and bot tokens. GitHub's secret scanning catches these. **Before running backup, sanitize memory files** — use `memory(action='replace')` to swap key-containing entries for generic references ("stored in config files"). This is the most common cause of backup failures.
5. **If error occurs mid-push**: The secret is in commit history. You need to either:
   - Create a new repo (cleanest)
   - Use `git filter-branch` or `BFG Repo-Cleaner` to remove the secret from history
   - GitHub also allows you to unblock via the web UI (Settings → Code security → Push protection rules)

### Force Push

Use `--force` to overwrite previous backup (keeps repo small):
```bash
git push --force origin main
```

## Cron Scheduling

### Using Hermes Cron

```
cronjob create --name "Hermes Backup" --schedule "every 6h" --prompt "Run backup script"
```

### Using System Cron

```bash
# Edit crontab
crontab -e

# Add line (every 6 hours)
0 */6 * * * /path/to/backup_script.sh >> /var/log/hermes_backup.log 2>&1
```

## Restore Process

1. Clone the backup repo:
   ```bash
   git clone https://github.com/user/repo.git /tmp/hermes_restore
   ```

2. Copy files back to Hermes directory:
   ```bash
   cp -r /tmp/hermes_restore/memories ~/.hermes/
   cp -r /tmp/hermes_restore/skills ~/.hermes/
   cp -r /tmp/hermes_restore/cron ~/.hermes/
   cp /tmp/hermes_restore/kanban.db ~/.hermes/
   cp /tmp/hermes_restore/config.yaml ~/.hermes/
   cp /tmp/hermes_restore/SOUL.md ~/.hermes/
   ```

3. Restart Hermes services

## Troubleshooting

| Issue | Cause | Fix |
|-------|-------|-----|
| Push rejected (secrets) | state.db or memories/ contain tokens | Exclude state.db; sanitize MEMORY.md before push |
| Permission denied | Wrong token or repo URL | Verify token has repo access |
| Nothing to commit | No changes since last backup | Normal — backup is current |
| Cron not running | Hermes cron service down | Check `cronjob list` status |
| Port 22 blocked | SSH not available | Use HTTPS with token in URL |
