import logging
import os

from opentelemetry import _logs
from opentelemetry.exporter.otlp.proto.http._log_exporter import (
    OTLPLogExporter,
)
from opentelemetry.exporter.otlp.proto.http.metric_exporter import (
    OTLPMetricExporter,
)
from opentelemetry.exporter.otlp.proto.http.trace_exporter import (
    OTLPSpanExporter,
)
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.logging import LoggingInstrumentor
from opentelemetry.sdk._logs import LoggerProvider, LoggingHandler
from opentelemetry.sdk._logs.export import BatchLogRecordProcessor
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.trace import set_tracer_provider


_INITIALIZED = False
logger = logging.getLogger(__name__)


def _env_flag(name: str, default: bool = False) -> bool:
    value = os.environ.get(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


def _otlp_enabled() -> bool:
    # Explicit switch has priority.
    if "OTEL_ENABLE_OTLP" in os.environ:
        return _env_flag("OTEL_ENABLE_OTLP", default=False)

    # Backward-compatible fallback: if endpoint is explicitly set to
    # non-localhost, enable OTLP automatically.
    endpoint = os.environ.get(
        "OTEL_EXPORTER_OTLP_ENDPOINT",
        "",
    ).strip().lower()
    return bool(endpoint and endpoint != "http://localhost:4318")


def _resource(service_name: str) -> Resource:
    return Resource.create(
        {
            "service.name": service_name,
            "service.version": os.environ.get("SERVICE_VERSION", "1.0.0"),
            "deployment.environment": os.environ.get(
                "DEPLOYMENT_ENV",
                "development",
            ),
        }
    )


def setup_observability(service_name: str) -> None:
    global _INITIALIZED
    if _INITIALIZED:
        return

    resource = _resource(service_name)

    LoggingInstrumentor().instrument(set_logging_format=True)

    if not _otlp_enabled():
        logger.info(
            "OTLP exporters are disabled "
            "(set OTEL_ENABLE_OTLP=true to enable)."
        )
        _INITIALIZED = True
        return

    try:
        tracer_provider = TracerProvider(resource=resource)
        tracer_provider.add_span_processor(
            BatchSpanProcessor(OTLPSpanExporter()),
        )
        set_tracer_provider(tracer_provider)

        metric_reader = PeriodicExportingMetricReader(OTLPMetricExporter())
        MeterProvider(resource=resource, metric_readers=[metric_reader])

        logger_provider = LoggerProvider(resource=resource)
        logger_provider.add_log_record_processor(
            BatchLogRecordProcessor(OTLPLogExporter()),
        )
        _logs.set_logger_provider(logger_provider)

        otel_log_handler = LoggingHandler(
            level=logging.INFO,
            logger_provider=logger_provider,
        )
        root_logger = logging.getLogger()
        root_logger.addHandler(otel_log_handler)
    except Exception as exc:
        logger.warning("Failed to initialize OTLP exporters: %s", exc)

    _INITIALIZED = True


def instrument_fastapi_app(app) -> None:
    FastAPIInstrumentor.instrument_app(app)
