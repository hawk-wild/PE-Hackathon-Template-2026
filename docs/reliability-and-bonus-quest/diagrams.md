# Reliability Diagrams

This page contains reliability-focused diagrams: error handling, recovery, and observability loops.

## 1. Error Handling Decision Flow

```mermaid
flowchart TD
  Req[Incoming request] --> Val{Schema valid?}
  Val -- No --> E422[Return 422]
  Val -- Yes --> Logic{Business rule passes?}
  Logic -- No --> E4xx[Return 400 or 404]
  Logic -- Yes --> Exec[Execute route logic]
  Exec --> Crash{Unhandled exception?}
  Crash -- Yes --> E500[Global handler returns 500 JSON]
  Crash -- No --> Ok[Return success response]
```

## 2. Fleet Startup and Recovery Flow

```mermaid
flowchart TD
  DB[(PostgreSQL)] --> Init[app-init]
  Redis[(Redis)] --> Init
  Init --> A1[app-1]
  Init --> A2[app-2]
  Init --> A3[app-3]
  A1 --> LB[NGINX]
  A2 --> LB
  A3 --> LB
  Fail{Replica failure?} -->|yes| Recover[Restart failed replica]
  Recover --> LB
  Fail -->|no| LB
```

## 3. Reliability Observability Feedback Loop

```mermaid
flowchart LR
  Traffic[Client traffic] --> App[FastAPI App]
  App --> Logs[Structured JSON Logs]
  App --> Metrics[Metrics and diagnostics]
  Logs --> Detect[Detection and diagnosis]
  Metrics --> Detect
  Detect --> Action[Mitigation and recovery]
  Action --> App
```

## 4. Dependency Health Startup Flow

```mermaid
sequenceDiagram
  participant D as PostgreSQL
  participant C as Docker Compose
  participant A as App Service

  C->>D: Start database container
  D-->>C: Healthcheck passes (pg_isready)
  C->>A: Start app service
  A->>D: Initialize metadata and session pool
  D-->>A: Ready for queries
  A-->>C: Application healthy
```
