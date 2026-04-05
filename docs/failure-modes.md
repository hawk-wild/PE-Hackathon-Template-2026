# Failure Modes

This document catalogs likely failure scenarios and the current mitigation strategy implemented in this repository.

## Failure Matrix

| Failure Mode | Detection | Current Behavior | Mitigation Implemented |
|---|---|---|---|
| Invalid request payload | FastAPI/Pydantic validation | `422` JSON with `detail` array | Schema-based validation in request models |
| Missing referenced data (user/url) | Route logic checks | `404` JSON with explicit message | Early existence checks before mutation |
| Unsupported upload type | Route validation | `400` JSON (`Only CSV files allowed`) | Content/filename gate in bulk upload route |
| Unhandled application exception | Global exception handler | `500` JSON (`Internal Server Error`) | Exception normalization to avoid leaks |
| DB connection stale/dead | SQLAlchemy pool checkout | Retry with pre-ping validation | `pool_pre_ping=True` in DB engine |
| App process crash in container | Process exit/logs/healthcheck | Process restarted in-container | Restart loop in `docker-entrypoint.sh` |
| Container restart/host reboot | Docker runtime | Container auto-restarted | `restart: unless-stopped` in compose |

## Application-Level Failures

### Input and Contract Failures

- `422`: malformed request payloads
- `400`: unsupported file upload in `POST /users/bulk`
- `404`: missing resources and unknown routes

These paths keep failure responses predictable for clients and are covered by tests.

### Unexpected Exceptions

Unhandled exceptions are mapped to a safe, generic JSON response:

```json
{"detail": "Internal Server Error"}
```

The same failures are still logged through observability middleware/handlers.

## Runtime and Infrastructure Failures

### Process Crash (Inside App Container)

The app entrypoint is a simple supervisor loop:

1. Start uvicorn.
2. If uvicorn exits, log status.
3. Sleep 1 second.
4. Restart uvicorn.

This improves resilience to transient process-level crashes without requiring an immediate container restart.

### Container Failure

Both `app` and `db` services use:

```yaml
restart: unless-stopped
```

This gives baseline self-healing at container orchestration level.

### Dependency Startup Ordering

`app` waits for healthy `db`:

- DB healthcheck uses `pg_isready`
- `depends_on` is configured with `condition: service_healthy`

This reduces startup race failures where app boots before the database can accept connections.

## Known Reliability Gaps

- No explicit readiness endpoint distinct from liveness.
- No circuit breaker/retry policy at application call level (future concern if external dependencies are added).
- No autoscaling policy documented yet.
- No alerting pipeline attached to `/metrics` and `/logs` data.

## Related Documents

- `docs/error-handling.md`
- `docs/observability.md`
- `docs/resilience-runbook.md`
- `docs/reliability-bonus-quest.md`

