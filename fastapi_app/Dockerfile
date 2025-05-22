# Stage 1: ARM64-optimized builder
FROM --platform=linux/arm64 python:3.10-slim-bookworm as builder

# M3-specific optimizations
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    UVICORN_WORKERS=4  

# Install system dependencies with ARM64 optimizations
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq-dev \
    libjpeg-dev libopenblas-dev \  
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Python dependencies with M3-optimized wheels
COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install --user --extra-index-url https://rospypi.github.io/simple/ \ 
    -r requirements.txt

# Stage 2: Minimal production image
FROM --platform=linux/arm64 python:3.10-slim-bookworm

WORKDIR /app

# Copy Python env from builder
COPY --from=builder --chown=1000:1000 /root/.local /home/appuser/.local
COPY --from=builder /app/requirements.txt .

# M3-specific environment tuning
ENV PATH=/home/appuser/.local/bin:$PATH \
    PYTHONOPTIMIZE=2 \  
    OPENBLAS_NUM_THREADS=4 \  
    UVICORN_THREADS=2 

# Create optimized non-root user
RUN adduser \
    --disabled-password \
    --gecos "" \
    --home /home/appuser \
    --uid 1000 \
    appuser && \
    chown -R appuser:appuser /app

USER appuser

# Copy application
COPY --chown=appuser:appuser main.py .
COPY --chown=appuser:appuser templates/ ./templates/

# Health check with fast timeout
HEALTHCHECK --interval=10s --timeout=2s --start-period=5s \
    CMD curl -f http://localhost:8000/health || exit 1

EXPOSE 8000

# Maximum-performance UVicorn config for M3
CMD ["uvicorn", "main:app", \
    "--host", "0.0.0.0", \
    "--port", "8000", \
    "--workers", "4", \              
    "--loop", "uvloop", \             
    "--http", "httptools", \          
    "--no-access-log", \              
    "--timeout-keep-alive", "5"]     