# Observability

## Overview

The application ships with built-in observability primitives focused on hackathon-friendly reliability diagnostics:

- Structured JSON logging
- Lightweight system/process metrics endpoint
- Recent log retrieval endpoint
- Request timing and status logging middleware

## Structured Logging

`app/observability.py` configures a root logger with:

- JSON formatter for machine readability
- stdout stream handler for container logs
- rotating file handler for local persistence

Environment variables:

| Variable | Default | Purpose |
|---|---|---|
| `LOG_LEVEL` | `INFO` | Global log verbosity |
| `LOG_FILE` | `logs/app.log` | Log file path |
| `LOG_MAX_BYTES` | `2097152` | Rotation size threshold |
| `LOG_BACKUP_COUNT` | `5` | Number of rotated files retained |

Example log payload:

```json
{
  "timestamp": "2026-04-05T11:22:33.123456+00:00",
  "level": "INFO",
  "logger": "app",
  "message": "HTTP request",
  "component": "http",
  "method": "GET",
  "path": "/health",
  "status_code": 200,
  "duration_ms": 1.23
}
```

## Request Logging Middleware

`run.py` adds an HTTP middleware that logs per-request telemetry:

- HTTP method
- URL path
- response status code
- request duration (ms)
- client IP (if available)

Unhandled exceptions are logged with stack traces through `logger.exception`.

## Metrics Endpoint

`GET /metrics`

Returns snapshot telemetry from `psutil`:

- CPU percent and core count
- memory totals/usage
- process PID, RSS memory, and thread count
- server-side timestamp

This endpoint is intentionally simple and JSON-based for quick diagnostics.

## Logs Endpoint

`GET /logs?limit=<n>`

- Reads tail lines from configured log file.
- Parses valid JSON lines into objects.
- Returns raw fallback for non-JSON lines.
- Enforces `1 <= limit <= 1000`.

Use this during incidents to inspect recent failures without opening container shell access.

## Container and Runtime Integration

- JSON logs are sent to stdout, so `docker compose logs` remains useful.
- File rotation avoids unbounded log growth when writing to local files.

## Validation

Observability behavior is validated in `tests/test_observability.py`:

- JSON formatter includes structured fields
- log tail reader handles JSON + raw lines
- metrics function returns expected schema
- logger setup creates file and writes entries
