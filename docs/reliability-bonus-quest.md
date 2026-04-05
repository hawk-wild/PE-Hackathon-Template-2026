# Bonus Quest: Reliability Engineering

## Objective

Document and justify the reliability features implemented in this project, with direct mapping to code and test evidence.

## Reliability Controls Implemented

| Area | Implementation | Why It Improves Reliability |
|---|---|---|
| Global error normalization | FastAPI global exception handler returns stable `500` JSON | Prevents crash detail leakage and keeps client behavior predictable |
| Input validation | Pydantic request schemas and FastAPI validation | Rejects bad data early (`422`) and protects downstream logic |
| Explicit resource checks | Route-level `404` handling for missing users/urls | Avoids inconsistent writes and undefined behavior |
| Background event logging | URL create/update logs are written in background tasks | Keeps main request path responsive under moderate load |
| DB connection pool hardening | SQLAlchemy `pool_pre_ping`, `pool_size`, `max_overflow`, `pool_timeout` | Reduces errors from stale connections and connection starvation bursts |
| Structured logging | JSON logs to stdout and rotating file | Makes debugging and incident triage faster and machine-friendly |
| Runtime diagnostics | `/metrics` and `/logs` endpoints | Enables live health inspection without attaching debugger |
| Service liveness | `/health` endpoint and Docker healthchecks | Provides active signal for probes and operator checks |
| Process restart loop | Entrypoint re-launches uvicorn if it exits | Recovers from app process crashes inside the container |
| Container auto-restart | `restart: unless-stopped` for app and db | Improves resilience during daemon/host disruptions |

## Code Evidence Map

| Capability | File |
|---|---|
| App-level exception handling | `app/__init__.py` |
| Main runtime middleware and exception logging | `run.py` |
| DB pool configuration | `app/database.py` |
| Observability primitives | `app/observability.py` |
| Health endpoint | `app/routes/health.py` |
| Route-level error behavior (`users`) | `app/routes/users.py` |
| Route-level error behavior + background tasks (`urls`) | `app/routes/urls.py` |
| Compose healthchecks and restart policy | `compose.yaml` |
| Process supervisor loop | `docker-entrypoint.sh` |

## Test Evidence Map

| Reliability Behavior | Test File |
|---|---|
| 400/404/422/500 API error behavior | `tests/test_error_handling.py` |
| Health endpoint contract | `tests/test_health.py` |
| Event consistency and integration flow | `tests/test_integration.py` |
| JSON log format, metrics shape, log ingestion | `tests/test_observability.py` |
| Utility reliability (`generate_short_code` uniqueness) | `tests/test_utils.py` |

## Verification Result

Local execution:

```bash
python -m pytest -q
```

Observed result:

- `17 passed`
- Coverage `91.42%` (required threshold: `>=70%`)

## Operational Validation (Chaos Drill)

1. Start containers:

```bash
docker compose up -d --build
```

2. Confirm healthy services:

```bash
docker compose ps
```

3. Kill uvicorn process inside app container:

```bash
docker exec hackathon-app sh -c 'pkill -f "uvicorn run:app"'
```

4. Observe auto-restart in app logs:

```bash
docker compose logs -f app
```

5. Re-check availability:

```bash
curl http://127.0.0.1:8080/health
```

Expected: service returns `{"status": "ok"}` after recovery.

## Reliability Decisions and Trade-offs

- Chosen simplicity over orchestration complexity: restart loop + compose restart is enough for hackathon scope.
- Event writes are asynchronous for responsiveness, with eventual consistency in event history.
- Error payloads are intentionally compact and stable for API consumers.

## Future Hardening (Post-Hackathon)

- Add dedicated readiness endpoint with DB connectivity check.
- Add request IDs and trace IDs in logs for distributed debugging.
- Expose Prometheus-native metrics format for scraping.
- Add alerting thresholds for error rate and restart frequency.
- Add retry/backoff strategy for critical background tasks.
