import logging

from fastapi import FastAPI
from prometheus_fastapi_instrumentator import Instrumentator

from app.api.routes import router
from app.core.config import get_settings
from app.core.logging import configure_logging
from app.core.telemetry import configure_telemetry

settings = get_settings()
configure_logging(settings.log_level, settings.log_file)

app = FastAPI(title=settings.app_name)
configure_telemetry(
    app,
    settings.otel_exporter_otlp_endpoint,
    settings.otel_service_name,
)
Instrumentator().instrument(app).expose(app)
app.include_router(router)

logger = logging.getLogger(__name__)


@app.on_event("startup")
def on_startup() -> None:
    logger.info(
        "application startup complete",
        extra={"event": "startup", "environment": settings.app_env},
    )


@app.on_event("shutdown")
def on_shutdown() -> None:
    logger.info("application shutdown", extra={"event": "shutdown"})
