# Resilience and Recovery

## Reliability mechanisms

### 1. Database connection resilience

Configured in `app/database.py`:

- `pool_size` (default 20)
- `max_overflow` (default 10)
- `pool_timeout` (default 30)
- `pool_pre_ping=True`

Impact:

- stale connections are detected before use
- controlled behavior under connection pressure

### 2. Fleet resilience through service orchestration

`compose.yaml` runs one-time initialization (`app-init`) and three serving replicas (`app-1`, `app-2`, `app-3`) behind NGINX.

Impact:

- failures on one replica do not fully take down the service
- startup schema setup and optional seeding run once before traffic-serving replicas begin

### 3. Service health checks

- `/health` endpoint returns `{"status": "ok"}`
- DB healthcheck uses `pg_isready`
- Redis healthcheck verifies cache availability

Impact:

- startup dependency ordering and liveness verification become deterministic

### 4. Safe async event logging and cache fallback

URL workflows emit events through FastAPI background tasks, and cache operations are wrapped to fail open.

Impact:

- request responses are not blocked by non-critical event persistence
- Redis outages degrade performance, not correctness

## Recovery runbook (quick)

1. Check service state:

```bash
docker compose ps
```

2. Inspect application logs:

```bash
docker compose logs --tail=200 app-1 app-2 app-3
```

3. Verify app responsiveness:

```bash
curl http://localhost:8000/health
```

4. Inspect diagnostics:

```bash
curl http://localhost:8000/metrics
curl http://localhost:8000/metrics/json
```

## Known limitations

- No explicit readiness endpoint that performs DB and Redis dependency checks.
- No distributed tracing IDs in request logs.
- No retry queue/dead-letter behavior for background task failures.

These are acceptable for current scope but should be included in future hardening work.
