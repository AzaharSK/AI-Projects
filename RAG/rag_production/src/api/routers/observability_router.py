"""
/health  and  /metrics  endpoints — observability layer.
"""

from fastapi import APIRouter, Request

from src.api.schemas.schemas import HealthResponse, MetricsResponse, VectorStoreMetrics

router = APIRouter(tags=["Observability"])


@router.get("/health", response_model=HealthResponse, summary="Overall service health")
async def health(request: Request) -> HealthResponse:
    """
    Returns system status.

    - ``status: "ok"`` — fully initialised, ready to accept queries.
    - ``status: "initialising"`` — no documents ingested yet.

    Suitable for Kubernetes liveness/readiness probes.
    """
    data = request.app.state.orchestrator.health()
    return HealthResponse(**data)


@router.get("/liveness", summary="Kubernetes liveness probe")
async def liveness():
    """
    Checks whether process is alive.

    Kubernetes uses this to determine whether
    container should be restarted.
    """

    return {"alive": True}

@router.get("/readiness", summary="Kubernetes readiness probe")
async def readiness(request: Request):
    """
    Checks if application is ready
    to serve requests.

    Useful for:

    - vectorstore loaded
    - graph initialized
    - embeddings available
    """

    orchestrator = request.app.state.orchestrator
    ready = orchestrator.is_ready

    return {
        "ready": ready,
        "status":
            "ready"
            if ready
            else "initialising"
    }

@router.get("/app-metrics", response_model=MetricsResponse, summary="Runtime metrics")
async def metrics(request: Request) -> MetricsResponse:
    """
    Lightweight operational metrics:

    - query throughput & average latency
    - ingest job count
    - vector store chunk count and index build time
    """
    data = request.app.state.orchestrator.metrics()
    vs = VectorStoreMetrics(**data.pop("vectorstore"))
    return MetricsResponse(**data, vectorstore=vs)
