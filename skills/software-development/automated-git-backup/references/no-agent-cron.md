# no_agent Cron Mode in Hermes

## Overview

When `no_agent: true` is set on a cron job, the scheduler runs the script **directly** without invoking an LLM. The script's stdout is delivered verbatim as the message.

## When to Use

- **Backups / sync scripts** — deterministic, no reasoning needed
- **Health checks / watchdogs** — threshold alerts, disk/memory/GPU monitoring
- **API pollers with fixed output shape** — CI notifications, price feeds
- **Any script that produces exact message text** — no summarization, no conditional logic

## When NOT to Use

- Anything requiring reasoning (summarize a feed, pick interesting items, conditional logic based on content)
- Tasks needing user interaction
- Dynamic decision-making based on content

## Requirements

- `script` MUST be set (relative to `~/.hermes/scripts/`)
- `prompt` and `skills` are ignored
- `no_agent: true` explicitly

## Delivery Semantics

1. **Non-empty stdout** → sent verbatim as message
2. **Empty stdout** → SILENT (nothing delivered) — design scripts to stay quiet when nothing to report
3. **Non-zero exit / timeout** → error alert sent (watchdog can't fail silently)

## Example: Backup Script Cron

```python
cronjob(
    action="create",
    name="Hermes Auto Backup (every 6 hours)",
    schedule="0 */6 * * *",
    script="backup_hermes.sh",  # In ~/.hermes/scripts/
    no_agent=True,
    deliver="origin"
)
```

## Debugging

- Check cron execution: `cronjob action=list`
- View last run: `cronjob action=run job_id=<id>` (manual trigger)
- Script logs: Check `~/.hermes/logs/cron/` or script's own logging

## Key Difference from Agent Mode

| Aspect | Agent Mode (default) | no_agent Mode |
|--------|---------------------|---------------|
| LLM Call | Every tick | Never |
| Auth/Provider | Required | Not needed |
| Output | Agent summary | Script stdout verbatim |
| Empty output | "No changes" message | SILENT |
| Error handling | Agent reports | Exit code → alert |
| Use case | Reasoning tasks | Deterministic scripts |