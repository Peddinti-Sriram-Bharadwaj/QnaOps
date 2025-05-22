# Stage 1: ARM64-optimized builder (now dependency-free)
FROM --platform=linux/arm64 python:3.10-slim-bookworm as builder

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    UVICORN_WORKERS=4

WORKDIR /app

COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install --user -r requirements.txt  # No need for rospypi now

# Stage 2: Minimal production image
FROM --platform=linux/arm64 python:3.10-slim-bookworm

WORKDIR /app
COPY --from=builder --chown=1000:1000 /root/.local /home/appuser/.local
COPY --from=builder /app/requirements.txt .

ENV PATH=/home/appuser/.local/bin:$PATH \
    PYTHONOPTIMIZE=2 \
    UVICORN_THREADS=2

RUN adduser \
    --disabled-password \
    --gecos "" \
    --home /home/appuser \
    --uid 1000 \
    appuser && \
    chown -R appuser:appuser /app

USER appuser
COPY --chown=appuser:appuser main.py .
COPY --chown=appuser:appuser templates/ ./templates/

EXPOSE 8000
CMD ["uvicorn", "main:app", \
    "--host", "0.0.0.0", \
    "--port", "8000", \
    "--workers", "4", \
    "--loop", "uvloop", \
    "--http", "httptools", \
    "--no-access-log", \
    "--timeout-keep-alive", "5"]