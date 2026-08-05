# Hermes Agent Version Updates

## Overview

Hermes Agent can be updated via several paths depending on installation method.

## Installation Methods & Update Commands

### 1. Shell Installer (recommended, most common)

```bash
# Re-run installer — handles version detection, migration, uv sync
curl -fsSL https://hermes-agent.nousresearch.com/install.sh | bash
```

### 2. Git Source Install (`/opt/hermes-agent` or similar)

```bash
cd /opt/hermes-agent
git fetch origin --tags
git checkout main          # or specific tag: git checkout v2026.8.3
pip install -e .           # Reinstall package in editable mode
```

### 3. Pip Install (if published)

```bash
pip install --upgrade hermes-agent
```

### 4. Desktop App (Electron)

Auto-updates via built-in updater, or re-run installer.

## Version Schemes

| Scheme | Format | Example | Source |
|--------|--------|---------|--------|
| **Release tags** | `vYYYY.M.D[.N]` | `v2026.8.3` | Git tags |
| **PyPI package** | `X.Y.Z` | `0.20.0` | `pyproject.toml` |
| **Dev/main branch** | `X.Y.Z-dev` | `0.20.0` (188 commits ahead) | `pyproject.toml` |

**Note:** The `pyproject.toml` version often stays the same between releases; tags are the authoritative release markers.

## Checking Current Version

```bash
hermes --version
# Output: Hermes Agent v0.20.0 (2026.8.3)
#                 ^package    ^release tag
```

## Checking for Updates

```bash
# Via CLI (if configured)
hermes version

# Manual check
cd /opt/hermes-agent
git fetch origin --tags
git tag --sort=-version:refname | head -5
git log --oneline -1 origin/main
```

## Update Workflow (Git Source)

```bash
# 1. Fetch latest
cd /opt/hermes-agent
git fetch origin --tags

# 2. See what's new
git log --oneline HEAD..origin/main | head -20
git tag --sort=-version:refname | head -5

# 3. Choose target
# Option A: Latest release (stable)
git checkout v2026.8.3

# Option B: Bleeding edge (main branch)
git checkout origin/main

# 4. Reinstall
pip install -e .

# 5. Verify
hermes --version
```

## Restarting Services After Update

If running gateway/TUI/desktop:

```bash
# Stop gateway
pkill -f "gateway.run"

# Start fresh (or use hermes desktop / hermes --tui)
cd /opt/hermes-agent && python -m gateway.run &

# Or just restart your chat session — new process picks up new code
```

## Common Issues

| Problem | Fix |
|---------|-----|
| `ModuleNotFoundError: yaml` | `pip install pyyaml` or `pip install -e .` |
| Old config breaks | Run `hermes setup` or `hermes doctor` |
| Desktop app won't launch | Re-run installer; clears Electron cache |
| `hermes` command not found | `~/.local/bin` not in PATH; re-run installer |

## Our Session: v0.19.0 → v0.20.0 (main branch)

```bash
# Was on: 6deb92df5 (v0.19.0 era)
# Moved to: cc245e84d (origin/main, 188 commits ahead of v2026.8.3)
cd /opt/hermes-agent
git fetch origin --tags
git checkout origin/main
pip install -e .
# Result: Hermes Agent v0.20.0 (2026.8.3) — same package version, newer code
```