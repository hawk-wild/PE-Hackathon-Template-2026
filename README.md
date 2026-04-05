# Production Ready URL shortener

For detailed documentation, visit the published GitBook: https://hawk-wild.gitbook.io/untitled

Production-style URL shortener service built for the MLH PE Hackathon tracks:

- Reliability Engineering
- Scalability Engineering
- Incident Response
- Documentation

The app is implemented with FastAPI, SQLAlchemy, PostgreSQL, Redis, Nginx, Prometheus, Alertmanager, Grafana, pytest, and k6.

## Getting Started

### Prerequisites

- Python 3.13+
- `uv`
- Docker + Docker Compose for the full stack

Install `uv` if needed:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### Local Development

Install dependencies:

```bash
uv sync
```

Run the app:

```bash
uv run python run.py
```

Open:

- App: `http://127.0.0.1:8000`
- Health: `http://127.0.0.1:8000/health`

Quick check:

```bash
curl http://127.0.0.1:8000/health
```

Expected response:

```json
{"status":"ok"}
```

### Database Behavior

- Local startup falls back to SQLite using `app.db` when no external database is configured.
- Docker Compose uses PostgreSQL.
- Docker Compose also runs a one-time `app-init` container to create tables and seed baseline data before the app replicas start serving traffic.

### Full Docker Stack

Start everything:

```bash
docker compose up -d --build
docker compose ps
```

Main endpoints:

- App via Nginx: `http://127.0.0.1:8000`
- Prometheus: `http://127.0.0.1:9090`
- Alertmanager: `http://127.0.0.1:9093`
- Grafana: `http://127.0.0.1:3000`

Stop:

```bash
docker compose down
```

Clean reset:

```bash
docker compose down -v --remove-orphans
```

## API Endpoints

### Health

- `GET /health`

### Users

- `GET /users`
- `GET /users/{id}`
- `POST /users`
- `POST /users/bulk`
- `PUT /users/{id}`
- `DELETE /users/{id}`

### URLs

- `GET /urls`
- `GET /urls/{id}`
- `GET /urls/{short_code}/redirect`
- `POST /urls`
- `PUT /urls/{id}`
- `DELETE /urls/{id}`

### Events

- `GET /events`
- `POST /events`

### Observability

- `GET /metrics`
- `GET /metrics/json`

Detailed API contract:

- [API Reference](https://hawk-wild.gitbook.io/untitled/api-reference)

## Reliability Engineering

### Bronze

Implemented:

- pytest unit tests
- CI workflow for automated test execution
- working `GET /health`

Verify:

```bash
uv run pytest
curl http://127.0.0.1:8000/health
```

### Silver

Implemented:

- `pytest-cov`
- integration tests against the API and DB
- CI gate that blocks downstream deploy flow if tests fail
- documented `404` and `500` behavior

Key docs:

- [Error Handling Contract](https://hawk-wild.gitbook.io/untitled/error-handling-contract)
- [Reliability and Bonus Quest Overview](https://hawk-wild.gitbook.io/untitled/overview-1)

### Gold

Implemented:

- `70%` coverage gate
- graceful JSON validation errors
- chaos/restart demo support
- failure mode documentation
- hidden-edge reliability handling:
  - duplicate email and username rejection
  - short-code collision retry
  - inactive URL handling
  - malformed CSV handling
  - audit event creation for URL lifecycle actions

Key docs:

- [Resilience and Recovery](https://hawk-wild.gitbook.io/untitled/resilience-and-recovery)
- [Bonus Quest Validation Report](https://hawk-wild.gitbook.io/untitled/bonus-quest-report)
- [Reliability Diagrams](https://hawk-wild.gitbook.io/untitled/diagrams-1)

## Scalability Engineering

### Bronze

Load-test scripts included:

- `loadtest_bronze.js`
- `loadtest_silver.js`
- `loadtest_gold.js`

Run:

```bash
k6 run loadtest_bronze.js
```

### Silver

Implemented:

- 3 app replicas
- Nginx load balancer
- Docker Compose multi-service topology

Check running containers:

```bash
docker compose ps
```

### Gold

Implemented:

- Redis caching for hot API responses
- PostgreSQL + Redis + Nginx + multi-replica app topology
- load-tested 500+ concurrent users
- bottleneck tuning for DB initialization, connection pooling, and cache-backed reads

Latest verified Gold run:

- `p95 latency: 513.08ms`
- `http_req_failed: 3.32%`
- all endpoint checks passed in the k6 script

Run:

```bash
k6 run loadtest_gold.js
```

Target a custom URL:

```bash
BASE_URL=http://127.0.0.1:8000 k6 run loadtest_gold.js
```

Redis cache evidence:

```bash
docker compose exec redis redis-cli INFO stats
docker compose exec redis redis-cli INFO keyspace
docker compose exec redis redis-cli KEYS '*'
```

The strongest proof points are:

- `keyspace_hits`
- `keyspace_misses`
- `db0:keys=...`

Scalability docs:

- [Scalability, Observability, and Operations Overview](https://hawk-wild.gitbook.io/untitled/overview-2)
- [Load Testing Guide](https://hawk-wild.gitbook.io/untitled/load-testing)
- [Operations Playbook](https://hawk-wild.gitbook.io/untitled/operations-playbook)

## Incident Response

### Bronze

Implemented:

- structured JSON logging
- metrics endpoints


Verify:

```bash
curl http://127.0.0.1:8000/metrics/json
```

### Silver

Implemented:

- Prometheus alert rules
- Alertmanager routing
- Slack/Discord webhook placeholders
- manual alert testing support

Key files:

- [monitoring/prometheus/alert_rules.yml](monitoring/prometheus/alert_rules.yml)
- [monitoring/alertmanager/alertmanager.yml](monitoring/alertmanager/alertmanager.yml)
- [Monitoring and Alerting](https://hawk-wild.gitbook.io/untitled/monitoring-and-alerting)

### Gold

Implemented:

- Grafana dashboard
- command-center style observability stack
- emergency/runbook documentation
- logs + metrics driven diagnosis workflow

Key docs:

- [Monitoring and Alerting](https://hawk-wild.gitbook.io/untitled/monitoring-and-alerting)
- [Operations Playbook](https://hawk-wild.gitbook.io/untitled/operations-playbook)
- [Scalability and Monitoring Diagrams](https://hawk-wild.gitbook.io/untitled/diagrams-2)
- [monitoring/grafana/dashboards/gold-command-center.json](monitoring/grafana/dashboards/gold-command-center.json)

## Documentation Quest

### Bronze

Included:

- README setup guide
- API documentation
- architecture/diagram docs

### Silver

Included:

- deployment-oriented Docker flow
- troubleshooting/failure docs
- environment/config documentation

### Gold

Included:

- runbooks
- design/decision-oriented docs
- load/capacity proof through k6 results and scale-out docs

Documentation index:

- [Complete Documentation](https://hawk-wild.gitbook.io/untitled)
- [Architecture and API Overview](https://hawk-wild.gitbook.io/untitled/overview)
- [Reliability and Bonus Quest Overview](https://hawk-wild.gitbook.io/untitled/overview-1)
- [Scalability, Observability, and Operations Overview](https://hawk-wild.gitbook.io/untitled/overview-2)
- [Architecture Diagrams](https://hawk-wild.gitbook.io/untitled/diagrams)
- [Reliability Diagrams](https://hawk-wild.gitbook.io/untitled/diagrams-1)
- [Scalability and Monitoring Diagrams](https://hawk-wild.gitbook.io/untitled/diagrams-2)

## Testing

Run the complete suite:

```bash
uv run pytest
```

Coverage is enforced with:

- `pytest-cov`
- `--cov-fail-under=70`

## Environment Variables

Common variables used by the repo:

- `DATABASE_URL`
- `DATABASE_HOST`
- `DATABASE_PORT`
- `DATABASE_USER`
- `DATABASE_PASSWORD`
- `DATABASE_NAME`
- `REDIS_URL`
- `PORT`
- `HOST`
- `WEB_CONCURRENCY`
- `ENABLE_STARTUP_SEED`
- `RUN_DB_INIT_ON_STARTUP`
- `DB_POOL_SIZE`
- `DB_MAX_OVERFLOW`
- `DB_POOL_TIMEOUT`
- `DB_POOL_RECYCLE`
- `LOG_LEVEL`
- `LOG_FILE`
- `LOG_MAX_BYTES`
- `LOG_BACKUP_COUNT`
- `SLACK_WEBHOOK_URL`
- `DISCORD_WEBHOOK_URL`

Base example config lives in [.env.example](.env.example).

## Project Layout

```text
app/
  __init__.py
  cache.py
  database.py
  observability.py
  models/
  routes/
docs/
monitoring/
nginx/
seed_data/
tests/
compose.yaml
Dockerfile
loadtest_bronze.js
loadtest_silver.js
loadtest_gold.js
run.py
```

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE).
