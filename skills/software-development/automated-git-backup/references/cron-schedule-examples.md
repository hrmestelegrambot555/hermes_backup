# Common Cron Schedules for Backups

## Format

```
* * * * *
| | | | └── Day of week (0-7) (Sun=0 or 7)
| | | └──── Month (1-12)
| | └────── Day of month (1-31)
| └──────── Hour (0-23)
└────────── Minute (0-59)
```

## Common Backup Schedules

| Schedule | Cron Expression | Description |
|----------|----------------|-------------|
| Every 6 hours | `0 */6 * * *` | 00:00, 06:00, 12:00, 18:00 |
| Every 4 hours | `0 */4 * * *` | 00:00, 04:00, 08:00, 12:00, 16:00, 20:00 |
| Every hour | `0 * * * *` | Top of every hour |
| Daily at 2 AM | `0 2 * * *` | Low traffic time |
| Daily at 3:30 AM | `30 3 * * *` | Avoid midnight collisions |
| Twice daily | `0 2,14 * * *` | 2 AM and 2 PM |
| Weekdays only | `0 2 * * 1-5` | Mon-Fri at 2 AM |
| Weekly (Sunday) | `0 3 * * 0` | Sunday 3 AM |
| Monthly (1st) | `0 4 1 * *` | 1st of month at 4 AM |

## Hermes Cronjob Examples

```python
# Every 6 hours
cronjob(action="create", schedule="0 */6 * * *", script="/path/backup.sh")

# Daily at 2:30 AM
cronjob(action="create", schedule="30 2 * * *", script="/path/backup.sh")

# Weekdays at 3 AM
cronjob(action="create", schedule="0 3 * * 1-5", script="/path/backup.sh")
```

## Tips

- **Stagger multiple jobs** — don't run all at `0 0 * * *`
- **Use random minute** for distributed systems: `RANDOM % 60` in script
- **Log output** — redirect to file: `>> /var/log/backup.log 2>&1`
- **Test with `cronjob action=run job_id=...`** before relying on schedule