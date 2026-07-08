# Production Runbook

Operational checklist for deploying Core Dispatch in production.

## Pre-deployment

- [ ] Set all secrets in environment (never hardcode)
  - VAPI_API_KEY
  - WEBHOOK_SECRET
  - CALENDAR_API_KEY
  - NOTIFIER_URL
- [ ] Confirm calling window for your timezone (call_window_start, call_window_end)
- [ ] Set max_attempts to a safe limit (recommend: 3)
- [ ] Enable dry_run: true for first 24h and verify logs

## Holiday guard

Add skip-days to prevent calls on public holidays:

`python
config = DispatchConfig(
    skip_days=["2026-07-04", "2026-12-25", "2026-01-01"],
    call_window_start=9,
    call_window_end=17,
)
`

## Monitoring

- Watch dispatch.callback_queue.depth metric â€” if it grows, increase worker threads
- Alert on dispatch.lead.closed_lost_rate > 30% (signals bad lead quality)
- Alert on dispatch.webhook.hmac_fail > 0 (signals replay attack or misconfigured secret)

## Rollback

1. Stop dispatcher service
2. Export LeadStore snapshot
3. Redeploy previous version
4. Replay pending leads from snapshot

## Incident response

If leads stop advancing state:
1. Check voice provider uptime
2. Verify calling window hasn't expired for the day
3. Check max_attempts hasn't been hit fleet-wide
4. Inspect last 10 webhook events for error patterns
