# Resilience Runbook

## Purpose

This runbook provides operator steps to verify reliability behavior and quickly troubleshoot service instability.

## Prerequisites

- Docker installed
- Docker Compose available
- Project root as working directory

## Start Stack

```bash
docker compose up -d --build
docker compose ps
```

Expected:

- `hackathon-db` is healthy
- `hackathon-app` is running and healthy

## Baseline Health Checks

```bash
curl http://127.0.0.1:8080/health
curl http://127.0.0.1:8080/metrics
curl "http://127.0.0.1:8080/logs?limit=20"
```

Expected:

- `/health` returns `{"status": "ok"}`
- `/metrics` returns CPU/memory/process JSON
- `/logs` returns recent structured events

## Chaos Test: Kill Web Process

This validates in-container auto-restart behavior.

```bash
docker exec hackathon-app sh -c 'pkill -f "uvicorn run:app"'
docker compose logs -f app
```

Expected log pattern:

- uvicorn exits
- entrypoint reports restart
- uvicorn starts again

Re-verify service:

```bash
curl http://127.0.0.1:8080/health
```

## Failure Triage Checklist

1. Check container status: `docker compose ps`
2. Check app logs: `docker compose logs --tail=200 app`
3. Check DB logs: `docker compose logs --tail=200 db`
4. Check runtime diagnostics: `/metrics` and `/logs`
5. Verify DB reachability from app (if needed): inspect startup and request-time errors in logs

## Common Symptoms and Actions

| Symptom | Likely Cause | Immediate Action |
|---|---|---|
| Frequent 500 responses | Unhandled runtime exception | Inspect `/logs`, trace failing endpoint path |
| App unhealthy in compose | process crash loop | Check `app` logs for restart reason |
| Startup failure | DB not healthy/ready | Confirm DB healthcheck and app dependency state |
| Slow API responses | DB contention or heavy queries | Use request logs (`duration_ms`) and inspect load patterns |

## Post-Incident Notes Template

Use this after each incident:

- Timestamp:
- Impacted endpoints:
- Error codes observed:
- Root cause:
- Mitigation applied:
- Follow-up action items:
