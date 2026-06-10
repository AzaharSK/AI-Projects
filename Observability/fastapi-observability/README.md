# FastAPI Observability Skeleton (Prometheus + Loki + Promtail + Tempo + Grafana)

This project is a production-style learning skeleton for:
- FastAPI application runtime
- Structured success/error logs
- OpenTelemetry tracing
- Prometheus metrics
- Full observability stack with Docker Compose: Prometheus, Loki, Promtail, Tempo, Grafana, OpenTelemetry Collector

## Project Layout

- `app/` FastAPI application code
- `deploy/` service and observability config templates
- `docker-compose.yml` local observability stack orchestration
- `Dockerfile` FastAPI container image definition
- `pyproject.toml` Python dependencies managed by uv
- `.env.example` app environment template

## API Endpoints

- `GET /health` health status
- `GET /demo/success` emits success log and trace span
- `GET /demo/error` emits error log and returns HTTP 500
- `GET /demo/random` random success or error to generate mixed telemetry
- `GET /metrics` Prometheus metrics endpoint

## Run With Docker Compose

Assuming Docker and Docker Compose are already installed:

```bash
docker compose up -d --build
```

This will build the FastAPI image and start:
- FastAPI
- Prometheus
- Loki
- Promtail
- Tempo
- OpenTelemetry Collector
- Grafana

Docker commands:

```bash
docker compose ps
docker compose logs -f fastapi
docker compose down
```

Docker Compose will:
1. Build the FastAPI image
2. Start FastAPI, Prometheus, Loki, Promtail, Tempo, OpenTelemetry Collector, and Grafana

## Default Ports

- FastAPI: `8000`
- Prometheus: `9090`
- Grafana: `3000`
- Loki: `3100`
- Promtail: `9080`
- Tempo HTTP: `3200`
- Tempo OTLP gRPC ingest: `4317`
- OTel Collector OTLP HTTP ingest: `4318`

## Verify

```bash
curl http://127.0.0.1:8000/health
curl http://127.0.0.1:8000/metrics
curl http://127.0.0.1:8000/demo/success
curl http://127.0.0.1:8000/demo/error
curl http://127.0.0.1:8000/demo/random
curl http://127.0.0.1:9090/-/healthy
```

Check logs:

```bash
docker compose logs -f fastapi
```

Check container status:

```bash
docker compose ps
```

## Notes

- Grafana datasource provisioning is preconfigured for Prometheus, Loki, and Tempo.
- Log format is JSON and includes OpenTelemetry trace/span IDs for correlation.


<img width="1790" height="506" alt="image" src="https://github.com/user-attachments/assets/93537d01-660d-4459-b59b-5e5af394ea54" />

<img width="1758" height="128" alt="image" src="https://github.com/user-attachments/assets/7c80293d-56ff-480e-8056-fbfd0f1a30fb" />

<img width="1857" height="531" alt="image" src="https://github.com/user-attachments/assets/1c6d8651-5dc9-47c6-a978-6e92344765ed" />



# Create dashboard : Grafana --> Dashboards --> New --> New dashboard --> Add visualization.

### [1] Add Metrics panel (Prometheus)

- __Select datasource:__ Prometheus
- __Use query:__ `rate(http_requests_total[1m])`
- __If you want per-path:__ `sum by (handler, method, status)(rate(http_requests_total[5m]))`
- __Set visualization:__ Time series
- __Title:__ API Request Rate

### [2] Add Latency panel (Prometheus): --> New panel, datasource Prometheus
- __Query for p95:__
  ```
  histogram_quantile(0.95, sum by (le)
  (rate(http_request_duration_seconds_bucket[5m])))
  ```
- __Visualization:__ Time series
- __Title:__ API P95 Latency

### [3] Add Logs panel (Loki) : New panel -> datasource Loki
- __Query:__

```
{job="fastapi-observability"}

# Filter by app label
{job="fastapi-observability", app="fastapi"}
```
- __Visualization:__ Logs
- __Title:__ FastAPI Logs

### [4] Add Error Logs panel (Loki) : New panel, datasource Loki
- __Query:__ `{job="fastapi-observability"} |= "error"`
- __Visualization:__ Logs or Time series (if you use count over time): `sum(count_over_time({job="fastapi-observability"} |= "error"[5m]))`

```

# Only errors
{job="fastapi-observability"} |= "error"

# Count logs per minute
sum(count_over_time({job="fastapi-observability"}[1m]))

# Error count per minute
sum(count_over_time({job="fastapi-observability"} |= "error"[1m]))
```


- __Title:__ Error Logs


### [5] Add Traces flow (Tempo)
- Open Explore, select Tempo, search traces.
- From a trace, use “View logs for this span” and “View metrics for this span” to link signals.
- You can also add a TraceQL panel later if needed.

```bash
# All traces for your API service
{ resource.service.name = "fastapi-observability-api" }

# Errors only
{ resource.service.name = "fastapi-observability-api" && status = error }

# Health endpoint traces
{ resource.service.name = "fastapi-observability-api" && span.http.target = "/health" }

# Demo random endpoint traces
{ resource.service.name = "fastapi-observability-api" && span.http.target = "/demo/random" }

# Slow traces (example > 500ms)
{ resource.service.name = "fastapi-observability-api" && duration > 500ms }

```


### [6] Save dashboard
- Click Save dashboard, name it like `FastAPI Observability`.
- If you want, I can give you a ready-to-paste starter dashboard JSON with 6 panels (RPS, latency, error rate, logs stream, top endpoints, trace count).




<img width="1846" height="824" alt="image" src="https://github.com/user-attachments/assets/b17e3937-f73e-46de-aee8-7429884e572d" />


```bash
$ sudo apt update && sudo apt install -y apache2-utils

# Great, use ApacheBench with -n for 1000 requests.
# Recommended quick sequence:

# 1. Run load test
ab -n 1000 -c 50 http://127.0.0.1:8000/demo/random

# 2. Check FastAPI target is up in Prometheus
curl -s http://127.0.0.1:9090/api/v1/targets

# 3. Check request metric value
curl -s "http://127.0.0.1:9090/api/v1/query?query=sum(http_requests_total)"

# If you want higher RPS, increase concurrency:
ab -n 5000 -c 200 http://127.0.0.1:8000/demo/random

```

- This skeleton is intentionally simple but structured to reflect production service boundaries.
