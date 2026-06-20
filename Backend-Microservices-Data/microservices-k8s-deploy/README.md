# Microservices Kubernetes Deployment (Minikube + Ingress)

This project deploys three services and one ingress resource on Kubernetes:
- `service-b`: internal tax lookup API
- `service-a`: public price API that calls `service-b`
- `tax-calculator-frontend`: React/Vite frontend served by Nginx
- `microservices-ingress`: ingress routes for frontend and API

## Architecture

Ingress routing:
- `/api/(.*)` -> `service-a:3000` (rewritten to `/$1`)
- `/(.*)` -> `frontend:80`

Request flow:
1. Browser opens frontend via ingress URL (`http://<MINIKUBE_IP>/`).
2. Frontend calls backend using `/api/price?...`.
3. Ingress rewrites `/api/price` to `/price` and forwards to `service-a`.
4. `service-a` calls `service-b` using Kubernetes DNS (`http://service-b:4000`).

```mermaid
flowchart LR
  U[Browser] -->|http://MINIKUBE_IP/| I[NGINX Ingress]
  I -->|/(.*)| F[frontend Service\nClusterIP:80]
  F -->|frontend files| N[Frontend Pod\nNginx + React]
  U -->|/api/price| I
  I -->|rewrite /api/(.*) -> /$1| A[service-a Service\nClusterIP:3000]
  A --> AP[service-a Pod\nFastAPI]
  AP -->|http://service-b:4000/tax| B[service-b Service\nClusterIP:4000]
  B --> BP[service-b Pod\nFastAPI]
```

## Repository Structure

```text
k8s/
  frontend.yaml
  ingress.yaml
  service-a.yaml
  service-b.yaml
services/
  service-a/
  service-b/
tax-calculator-frontend/
```

## Service Details

### service-b (internal tax service)
- Code: `services/service-b/main.py`
- Endpoint: `GET /tax?country=<CODE>`
- Port: `4000`
- Kubernetes service type: `ClusterIP`

### service-a (price aggregator)
- Code: `services/service-a/main.py`
- Endpoint: `GET /price?amount=<number>&country=<CODE>`
- Port: `3000`
- Kubernetes service type: `ClusterIP`
- Environment variables:
  - `TAX_SERVICE_URL=http://service-b:4000`
  - `FRONTEND_URL=*`

### frontend (React/Vite + Nginx)
- App source: `tax-calculator-frontend/`
- Build arg: `VITE_API_URL`
- Recommended value for ingress mode: `/api`
- Runtime: Nginx on port `80`
- Kubernetes service type: `ClusterIP`

### ingress (public entry point)
- File: `k8s/ingress.yaml`
- Ingress class: `nginx`
- API path: `/api/(.*)` (regex)
- Frontend path: `/(.*)` (regex catch-all)

## Prerequisites

- Docker
- Minikube
- kubectl

## Deployment Steps

### 1) Start Minikube and enable ingress

```bash
minikube start
minikube addons enable ingress
kubectl get pods -n ingress-nginx
```

Wait until ingress controller pods are `Running`.

### 2) Build Docker images

```bash
cd microservices-k8s-deploy

docker build --no-cache -t service-b:latest services/service-b
docker build --no-cache -t service-a:latest services/service-a
docker build --no-cache \
  --build-arg VITE_API_URL=/api \
  -t tax-calculator-frontend:latest \
  tax-calculator-frontend
```

### 3) Load images into Minikube

```bash
minikube image load service-b:latest
minikube image load service-a:latest
minikube image load tax-calculator-frontend:latest
```

### 4) Apply Kubernetes manifests

```bash
kubectl apply -f k8s/
```

Expected resources include:
- `deployment/frontend`
- `deployment/service-a`
- `deployment/service-b`
- `service/frontend`
- `service/service-a`
- `service/service-b`
- `ingress/networking.k8s.io/microservices-ingress`

### 5) Verify deployments, services, ingress, and pods

```bash
kubectl get deployments,svc,ingress,pods
```

You should see:
- all deployments available
- all pods ready
- services as `ClusterIP`
- ingress resource present

### 6) Access the frontend

```bash
echo "http://$(minikube ip)/"
```

Open that URL in your browser.

## Smoke Tests

### API via ingress

```bash
curl "http://$(minikube ip)/api/price?amount=100&country=IN"
```

Example response:

```json
{
  "service": "A",
  "amount": 100.0,
  "tax": 18.0,
  "total": 118.0,
  "container": "service-a-xxxxxxxxxx-xxxxx",
  "service_b_container": "service-b-xxxxxxxxxx-xxxxx"
}
```

### Direct tax service check from inside cluster (optional)

```bash
kubectl run curl-test --rm -it --image=curlimages/curl -- \
  curl "http://service-b:4000/tax?country=IN"
```

## Request Lifecycle

1. User submits amount and country in frontend.
2. Frontend calls `/api/price?amount=<amount>&country=<country>`.
3. Ingress matches `/api/(.*)` and rewrites path to `/$1`.
4. `service-a` receives `/price`, calls `service-b` at `/tax`.
5. `service-a` computes total:

$$
total = amount + tax
$$

6. Result is returned to frontend and rendered in UI.

## Troubleshooting

### Ingress has no address or requests fail

```bash
kubectl get pods -n ingress-nginx
kubectl describe ingress microservices-ingress
```

If controller pods are not ready, wait a bit and retry.

### Frontend calls wrong backend URL

If the frontend image was built with an old `VITE_API_URL`, rebuild with:

```bash
docker build --no-cache \
  --build-arg VITE_API_URL=/api \
  -t tax-calculator-frontend:latest \
  tax-calculator-frontend
minikube image load tax-calculator-frontend:latest
kubectl rollout restart deployment/frontend
```

### Check logs

```bash
kubectl logs deployment/service-a --tail=100
kubectl logs deployment/service-b --tail=100
kubectl logs deployment/frontend --tail=100
```

## Notes

- `service-b` remains internal (`ClusterIP`) and is not exposed publicly.
- Ingress annotation `nginx.ingress.kubernetes.io/rewrite-target: /$1` removes `/api` before forwarding to `service-a`.
- The frontend default API base path is now `/api`, matching ingress routing.
