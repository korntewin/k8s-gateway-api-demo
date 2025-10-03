FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim AS python-base

WORKDIR /app
COPY pyproject.toml uv.lock /app/
COPY services/apiserver/pyproject.toml /app/services/apiserver/
COPY services/dagster_service/pyproject.toml /app/services/dagster_service/

RUN uv sync --all-packages --frozen --no-dev

FROM python-base AS apiserver
COPY services/apiserver /app/services/apiserver

ENV PYTHONPATH=/app/services

CMD ["uv", "run", "fastapi", "run", "/app/services/apiserver/api/rest/main.py", "--host", "0.0.0.0", "--port", "8000"]

FROM python-base AS dagster-codelocation
RUN apt-get update \
    && apt-get install -y --no-install-recommends openjdk-17-jre-headless \
    && rm -rf /var/lib/apt/lists/*

COPY services/apiserver /app/services/apiserver
COPY services/dagster_service /app/services/dagster_service

ENV PATH="/app/.venv/bin:${PATH}"
ENV PYTHONPATH=/app/services
ENV DAGSTER_HOME=/opt/dagster/dagster_home
ENV JAVA_HOME=/usr/lib/jvm/java-17-openjdk-amd64

RUN mkdir -p "${DAGSTER_HOME}"

CMD ["dagster-webserver", "-h", "0.0.0.0", "-p", "3000"]
