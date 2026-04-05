# Monitoring and Alerting

## Monitoring stack components

### Prometheus

Configured in `monitoring/prometheus/prometheus.yml`.

Responsibilities:

- scrape app metrics from `/metrics`
- scrape and evaluate every 5 seconds
- forward firing alerts to Alertmanager

### Alert rules

Defined in `monitoring/prometheus/alert_rules.yml`.

Current rules:

- `AppInstanceDown` (warning): one replica unreachable for 5 seconds
- `ServiceFleetDown` (critical): all replicas unreachable for 5 seconds
- `LoadBalancerDown` (critical): NGINX unreachable for 5 seconds
- `HighErrorRate` (critical): 5xx ratio over 3% for 5 seconds
- `HighLatencyP95` (warning): p95 latency over 2 seconds for 5 seconds
- `HighCPUReplica` (warning): per-replica CPU above 80% for 5 seconds

### Alertmanager

Configured in `monitoring/alertmanager/alertmanager.yml`.

Responsibilities:

- route critical alerts to on-call channel
- route warnings to non-paging channel
- inhibit noisy secondary alerts (`ServiceFleetDown` suppresses `AppInstanceDown`, and `LoadBalancerDown` suppresses `ServiceFleetDown`)

## Metrics exposure

The app exposes Prometheus metrics via instrumentation middleware when optional dependencies are available.

Required Python packages for `/metrics` exposure:

- `prometheus-fastapi-instrumentator`
- `prometheus_client`

If these packages are missing, Prometheus scrape on `/metrics` will fail and only JSON diagnostics endpoint `/metrics/json` remains available.

Additional JSON diagnostics endpoint exists at:

- `GET /metrics/json`

### Grafana

Grafana is included in the compose stack for dashboard visualization.

- URL: `http://localhost:3000`
- default credentials: `admin` / `admin`

## Notification channels

Environment-driven webhook substitution supports:

- Slack
- Discord (Slack-compatible webhook endpoint)

Runtime environment variables used in compose:

- `SLACK_WEBHOOK_URL`
- `DISCORD_WEBHOOK_URL`

## Validating alerts

Use manual or scripted methods described in `docs/manual-alert-testing.md`.

Common manual triggers:

```bash
docker compose stop app-1
docker compose stop app-1 app-2 app-3
docker compose stop nginx
```

## Production hardening recommendations

1. Pin image versions for Prometheus and Alertmanager (avoid `latest`).
2. Add authentication for Prometheus/Alertmanager UIs.
3. Add persistent dashboarding (Grafana) for trend analysis.
4. Store alert runbook links in alert annotations.
