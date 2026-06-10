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

<img width="1846" height="824" alt="image" src="https://github.com/user-attachments/assets/b17e3937-f73e-46de-aee8-7429884e572d" />

- This skeleton is intentionally simple but structured to reflect production service boundaries.
