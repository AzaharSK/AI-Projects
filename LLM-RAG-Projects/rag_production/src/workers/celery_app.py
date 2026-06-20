from celery import Celery

app = Celery(
    "rag",
    broker="redis://localhost:6379/0",
    backend="redis://localhost:6379/0"
)

app.autodiscover_tasks(
        ["src.workers"]
    )