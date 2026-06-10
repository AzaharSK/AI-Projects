import logging

from fastapi import APIRouter, HTTPException

from app.services.demo_service import DemoService

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/health")
def health() -> dict:
    logger.info("health check passed", extra={"event": "health"})
    return {"status": "ok"}


@router.get("/demo/success")
def demo_success() -> dict:
    return DemoService.success_event()


@router.get("/demo/error")
def demo_error() -> dict:
    try:
        return DemoService.fail_event()
    except RuntimeError as exc:
        logger.exception("demo.error endpoint failed")
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.get("/demo/random")
def demo_random() -> dict:
    try:
        return DemoService.random_event()
    except RuntimeError as exc:
        logger.exception("demo.random endpoint failed")
        raise HTTPException(status_code=500, detail=str(exc)) from exc
