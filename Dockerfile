FROM python:3.12-slim AS base

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

# Create non-root user before any chown to keep layers small.
RUN adduser --disabled-password --gecos "" appuser

# Copy build metadata FIRST so dependency installs can be cached separately
# from source changes. README is referenced by pyproject.toml's
# `readme = "README.md"` field, so it must be present at install time.
COPY pyproject.toml README.md ./
RUN pip install --no-cache-dir .

# Source last so layer cache invalidates only when src/ actually changes.
COPY src/ ./src/
COPY dashboard/ ./dashboard/

RUN chown -R appuser:appuser /app
USER appuser

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')" || exit 1

CMD ["uvicorn", "src.api.app:create_app", "--factory", "--host", "0.0.0.0", "--port", "8000"]
