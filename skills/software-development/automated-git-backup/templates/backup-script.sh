#!/bin/bash
# Automated Git Backup Script Template
# Copy and customize for your project

set -euo pipefail

# === CONFIGURATION ===
# Source directory to backup (e.g., /data/.hermes, /home/user/project)
SOURCE_DIR="/path/to/source"

# Destination git repo (local clone of remote)
REPO_DIR="/tmp/my_backup_repo"

# Git remote URL with auth (PAT or deploy key)
# Format: https://TOKEN@github.com/user/repo.git
GIT_REMOTE="https://ghp_YOUR_TOKEN@github.com/user/repo.git"

# Branch to push to (check remote: git branch -a)
BRANCH="master"

# Timestamp for commit message
TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')
HOSTNAME=$(hostname)

# === ALLOWLIST: Items to backup (explicit, relative to SOURCE_DIR) ===
BACKUP_ITEMS=(
    "config.yaml"
    "memories/"
    "skills/"
    "cron/"
    "kanban.db"
    "channel_directory.json"
    "gateway_state.json"
    "SOUL.md"
    "hooks/"
    "state/"
    # Add your items here
)

# === DENYLIST: Items to NEVER commit (relative to REPO_DIR after copy) ===
EXCLUDE_ITEMS=(
    "state.db"              # tokens
    "auth.json"             # credentials
    "*.cache.json"          # large caches
    ".env"                  # secrets
    "audio_cache/"
    "image_cache/"
    "cache/"
    "logs/"
    "sandboxes/"
    "pairing/"
    "platforms/"
    "bin/"
    "*.lock"
    "*.pid"
    "gateway_voice_mode.json"
    # Add your sensitive patterns here
)

echo "[$TIMESTAMP] Starting backup from $SOURCE_DIR to $REPO_DIR..."

# === ENSURE REPO EXISTS ===
if [ ! -d "$REPO_DIR/.git" ]; then
    echo "Cloning repo..."
    git clone "$GIT_REMOTE" "$REPO_DIR" 2>/dev/null || {
        echo "ERROR: Failed to clone repo. Check GIT_REMOTE and auth."
        exit 1
    }
fi

cd "$REPO_DIR"
git pull origin "$BRANCH" 2>/dev/null || true

# === COPY ALLOWLIST ITEMS ===
for item in "${BACKUP_ITEMS[@]}"; do
    src="$SOURCE_DIR/$item"
    dst="$REPO_DIR/$item"
    
    if [ -e "$src" ]; then
        echo "  Backing up: $item"
        rm -rf "$dst"
        cp -r "$src" "$dst"
    else
        echo "  Skipping (not found): $item"
    fi
done

# === REMOVE DENYLIST ITEMS ===
for item in "${EXCLUDE_ITEMS[@]}"; do
    dst="$REPO_DIR/$item"
    if [ -e "$dst" ]; then
        echo "  Removing excluded: $item"
        rm -rf "$dst"
    fi
done

# === CREATE BACKUP INFO ===
cat > "$REPO_DIR/backup_info.json" <<EOF
{
  "timestamp": "$TIMESTAMP",
  "hostname": "$HOSTNAME",
  "backup_items": $(printf '%s\n' "${BACKUP_ITEMS[@]}" | python3 -c 'import sys,json; print(json.dumps([line.strip() for line in sys.stdin]))')
}
EOF

# === COMMIT & PUSH IF CHANGES ===
if ! git diff --quiet || ! git diff --cached --quiet; then
    git add -A
    git config user.name "Backup Bot"
    git config user.email "backup@example.com"
    git commit -m "Auto backup: $TIMESTAMP"
    git push origin "$BRANCH"
    echo "[$TIMESTAMP] Backup pushed successfully"
else
    echo "[$TIMESTAMP] No changes to backup"
fi

echo "[$TIMESTAMP] Backup complete"