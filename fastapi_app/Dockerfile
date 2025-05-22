# Use an official Python runtime as a base image
FROM python:3.10-slim as builder

# Set environment variables for Python
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

# Install system dependencies only if needed (example: for psycopg2, you might need libpq-dev)
# RUN apt-get update && apt-get install -y --no-install-recommends libpq-dev && rm -rf /var/lib/apt/lists/*

# Copy only requirements first to leverage Docker cache
COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install --user -r requirements.txt

# --- Multi-stage build for a smaller final image ---
FROM python:3.10-slim

WORKDIR /app

# Copy installed Python packages from builder
COPY --from=builder /root/.local /root/.local
COPY --from=builder /app/requirements.txt .

# Ensure scripts in .local are usable
ENV PATH=/root/.local/bin:$PATH

# Copy application code
COPY main.py .
COPY templates/ ./templates/

# Expose the port (documentation only, does not publish it)
EXPOSE 8000

# Run as a non-root user for security
RUN useradd -m appuser && chown -R appuser /app
USER appuser

# Run Uvicorn (adjust workers if needed for production)
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]