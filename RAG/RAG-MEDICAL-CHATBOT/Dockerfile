## Parent image
FROM python:3.10-slim

ARG HTTP_PROXY
ARG HTTPS_PROXY
ARG NO_PROXY
ARG ALL_PROXY
ARG http_proxy
ARG https_proxy
ARG no_proxy
ARG all_proxy
ARG USE_PROXY=false

## Essential environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

## Work directory inside the docker container
WORKDIR /app

## Install dependencies (copy package source first because editable install needs it)
COPY requirements.txt setup.py ./
COPY app ./app
RUN set -eux; \
    if [ "${USE_PROXY}" = "true" ]; then \
        export HTTP_PROXY="${HTTP_PROXY:-${http_proxy:-}}"; \
        export HTTPS_PROXY="${HTTPS_PROXY:-${https_proxy:-}}"; \
        export NO_PROXY="${NO_PROXY:-${no_proxy:-}}"; \
        export ALL_PROXY="${ALL_PROXY:-${all_proxy:-}}"; \
        export http_proxy="${HTTP_PROXY}"; \
        export https_proxy="${HTTPS_PROXY}"; \
        export no_proxy="${NO_PROXY}"; \
        export all_proxy="${ALL_PROXY}"; \
    else \
        unset HTTP_PROXY HTTPS_PROXY NO_PROXY ALL_PROXY http_proxy https_proxy no_proxy all_proxy; \
    fi; \
    python -m ensurepip --upgrade || true; \
    python -m pip install --no-cache-dir --upgrade pip setuptools wheel; \
    python -m pip install --no-cache-dir -e .

## Copy application source
COPY . .

## Expose FastAPI port
EXPOSE 8000

## Run the FastAPI app
CMD ["uvicorn", "app.application:app", "--host", "0.0.0.0", "--port", "8000"]


