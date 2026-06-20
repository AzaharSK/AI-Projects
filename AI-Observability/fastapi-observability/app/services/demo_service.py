import logging
import random
import time

from opentelemetry import trace

logger = logging.getLogger(__name__)
tracer = trace.get_tracer(__name__)


class DemoService:
    @staticmethod
    def success_event() -> dict:
        with tracer.start_as_current_span("demo-success"):
            time.sleep(0.05)
            logger.info("demo.success completed", extra={"event": "success"})
            return {"status": "ok", "message": "Success path executed."}

    @staticmethod
    def fail_event() -> dict:
        with tracer.start_as_current_span("demo-fail"):
            time.sleep(0.05)
            logger.error("demo.fail simulated failure", extra={"event": "failure"})
            raise RuntimeError("Simulated failure for observability testing")

    @staticmethod
    def random_event() -> dict:
        with tracer.start_as_current_span("demo-random"):
            number = random.randint(1, 100)
            if number % 2 == 0:
                logger.info(
                    "demo.random success",
                    extra={"event": "random_success", "number": number},
                )
                return {"status": "ok", "number": number, "type": "success"}

            logger.error(
                "demo.random error",
                extra={"event": "random_error", "number": number},
            )
            raise RuntimeError(f"Random error path triggered with number={number}")
