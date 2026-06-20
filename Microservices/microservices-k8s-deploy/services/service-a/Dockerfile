FROM python:3.12-slim

WORKDIR /app

# ── Create virtual environment ────────────────────────────────────────────────
RUN python -m venv .venv
ENV VIRTUAL_ENV=/app/.venv \
    PATH="/app/.venv/bin:$PATH"

# ── Install dependencies (inline proxy override beats daemon-injected proxy) ──
COPY requirements.txt .
RUN http_proxy="" https_proxy="" HTTP_PROXY="" HTTPS_PROXY="" \
    pip install --no-cache-dir -r requirements.txt

COPY main.py .

EXPOSE 3000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "3000"]
