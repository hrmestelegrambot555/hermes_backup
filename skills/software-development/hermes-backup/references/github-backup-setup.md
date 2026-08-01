# GitHub Backup Integration Details

## Repository
- URL: `https://github.com/hrmestelegrambot555/hermes_backup`
- Branch: `master` (auto-created by git init)

## Authentication
- Classic Personal Access Token (ghp_...)
- Embedded in HTTPS URL: `https://${TOKEN}@github.com/user/repo.git`
- Port 22 blocked on this environment — must use HTTPS

## Backup Contents (verified)
- 553 files, ~14MB compressed
- Excludes: state.db, auth.json, .env (contain secrets)
- Includes: memories/, skills/, cron/, kanban.db, config.yaml, SOUL.md, state/, hooks/

## Push Protection Issue
GitHub detected the access token inside `state.db` (session data contains the token in plaintext).
Error: `GH013: Repository rule violations found — Push cannot contain secrets`

**Fix applied**: Removed `state.db` and `auth.json` from backup script.

### Critical: Push Protection Blocks Even Amended Commits

GitHub's secret scanning checks **ALL commits in the push**, not just the HEAD commit. Even if you:
- `git commit --amend` to remove the secret from the latest commit
- `git commit --fixup` or `git rebase -i` to remove from history

The secret still exists in the Git history, and GitHub will **reject the entire push**.

**Real fix options**:
1. **Fresh repo**: Create a new empty GitHub repo and push clean history
2. **Orphan branch**: `git checkout --orphan new_branch && git commit -m "clean"` then force push
3. **BFG Repo-Cleaner**: Use BFG to rewrite entire history (complex)

**Prevention**: Never commit secrets in the first place. Use `.gitignore` in the backup repo for sensitive files, or exclude them in the backup script before any commit.

## Cron Schedule
- Job ID: `752367e84023`
- Schedule: every 6 hours
- Next run: auto-calculated from creation time