# ---------- Build Stage ----------
FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim AS builder

WORKDIR /app

# Install build dependencies for compiling Python packages
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Configure UV for optimal performance
ENV UV_COMPILE_BYTECODE=1
ENV UV_LINK_MODE=copy
ENV UV_PYTHON_DOWNLOADS=never

# Copy dependency files and sync dependencies
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --locked --no-install-project --no-dev

# Copy source code selectively
COPY src/api ./src/api
COPY src/config.py ./src/config.py
COPY src/infrastructure ./src/infrastructure
COPY src/models ./src/models
COPY src/pipelines ./src/pipelines
COPY src/utils ./src/utils
COPY src/__init__.py ./src/__init__.py

# Also copy pyproject.toml and uv.lock for the final sync
COPY pyproject.toml uv.lock ./

# Install project dependencies into virtualenv
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --locked --no-dev


# ---------- Runtime Stage ----------
FROM python:3.12-slim-bookworm

# Copy built application and virtualenv from builder
COPY --from=builder /app /app

# Set Python path and environment variables
ENV PATH="/app/.venv/bin:$PATH"
ENV PYTHONPATH=/app
ENV HF_HOME=/tmp/huggingface
ENV FASTEMBED_CACHE=/tmp/fastembed_cache
ENV PORT=8000

# Create cache directories
RUN mkdir -p $HF_HOME $FASTEMBED_CACHE && chmod -R 755 $HF_HOME $FASTEMBED_CACHE

HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:$PORT/health || exit 1

# Expose backend port (8000)
EXPOSE $PORT

# Run FastAPI with uvicorn
# Use PORT env var (Cloud Run sets this) or default to 8000
CMD uvicorn src.api.main:app --host 0.0.0.0 --port ${PORT:-8000} --workers 1 --loop uvloop
