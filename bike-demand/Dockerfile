# Python patch and uv release are pinned for an auditable Lab 3 build.
FROM python:3.12.15-slim-bookworm

ARG SOURCE_REVISION
RUN test -n "$SOURCE_REVISION"
LABEL org.opencontainers.image.revision=$SOURCE_REVISION

COPY --from=ghcr.io/astral-sh/uv:0.12.23 /uv /uvx /bin/

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_PYTHON_DOWNLOADS=0 \
    BIKE_DEMAND_SOURCE_REVISION=${SOURCE_REVISION} \
    BIKE_DEMAND_SOURCE_CLEAN=true

WORKDIR /app

# Keep dependency installation cached while the application source changes.
COPY pyproject.toml uv.lock .python-version README.md ./
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --locked --no-install-project

# Copy only the Docker build context; .dockerignore removes host state.
COPY . .
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --locked --no-editable \
    && uv run --locked python -m bike_demand.preflight

# Lab 4 serves the trusted, evaluated model; training remains an explicit command.
EXPOSE 8000
CMD ["uv", "run", "--locked", "uvicorn", "bike_demand.api:app", "--host", "0.0.0.0", "--port", "8000"]
