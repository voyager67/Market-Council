FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    MC_DATABASE_PATH=/data/marketcouncil.sqlite3 \
    MC_ALLOWED_HOSTS=localhost,127.0.0.1

WORKDIR /app
COPY pyproject.toml README.md LICENSE ./
COPY src ./src
RUN python -m pip install --no-cache-dir --upgrade pip \
    && python -m pip install --no-cache-dir '.[api]' \
    && useradd --system --uid 10001 --create-home marketcouncil \
    && mkdir -p /data \
    && chown -R marketcouncil:root /data

USER 10001:0
VOLUME ["/data"]
EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/health', timeout=3).read()" || exit 1

CMD ["uvicorn", "marketcouncil.api:create_app", "--factory", "--host", "0.0.0.0", "--port", "8000"]
