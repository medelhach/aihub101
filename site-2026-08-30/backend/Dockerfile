FROM python:3.12-slim AS builder

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

COPY pyproject.toml ./
COPY app ./app
RUN python -m pip install --upgrade pip \
    && python -m pip wheel --wheel-dir /wheels .

FROM python:3.12-slim AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app
RUN addgroup --system --gid 1001 app \
    && adduser --system --uid 1001 --ingroup app app

COPY --from=builder /wheels /wheels
RUN python -m pip install --no-index --find-links=/wheels ai-intelligence-hub-api \
    && rm -rf /wheels

COPY alembic.ini ./
COPY migrations ./migrations
COPY entrypoint.py ./entrypoint.py

USER app
EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/api/v1/health/live')"

ENTRYPOINT ["python", "entrypoint.py"]
