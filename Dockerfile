# Multi-stage Dockerfile for ChipEngine
FROM python:3.11-slim AS builder

# Install uv for fast Python package management
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# Set working directory
WORKDIR /app

# Copy dependency files
COPY pyproject.toml .
COPY README.md .
COPY src ./src

# Install dependencies using uv
RUN uv venv && \
    . .venv/bin/activate && \
    uv pip install -e . && \
    uv pip install -e ".[production]"

# Production stage
FROM python:3.11-slim

# Install runtime dependencies including PostgreSQL client libraries
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user
RUN useradd -m -u 1000 chipengine

# Set working directory
WORKDIR /app

# Copy virtual environment from builder
COPY --from=builder /app/.venv /app/.venv
COPY --from=builder /app/src /app/src

# Copy application files
COPY pyproject.toml .
COPY README.md .

# Set environment variables
ENV PATH="/app/.venv/bin:$PATH"
ENV PYTHONUNBUFFERED=1
ENV UV_SYSTEM_PYTHON=1

# Create necessary directories
RUN mkdir -p /app/data && chown -R chipengine:chipengine /app

# Switch to non-root user
USER chipengine

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Default command - can be overridden
CMD ["uvicorn", "chipengine.api.app:app", "--host", "0.0.0.0", "--port", "8000"]