# ---- Stage 1: builder ----
FROM python:3.12-slim AS builder

WORKDIR /build

# Copy dependency manifest first to leverage layer cache
COPY requirements.txt .

RUN python -m venv /opt/venv && \
    /opt/venv/bin/pip install --no-cache-dir -r requirements.txt

# ---- Stage 2: runtime ----
FROM python:3.12-slim AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/opt/venv/bin:$PATH"

WORKDIR /app

# Virtualenv from builder — no pip/build toolchain in final image
COPY --from=builder /opt/venv /opt/venv

# Application code (changes often — copied last for cache)
COPY app/ app/
COPY templates/ templates/
COPY static/ static/

# Run as non-root
RUN useradd --create-home appuser && chown -R appuser /app
USER appuser

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
