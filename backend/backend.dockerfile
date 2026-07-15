ARG python=python:3.12-slim

# stage 1: build the virtualenv with uv
FROM ${python} AS builder

LABEL maintainer="Pooria Soltani <pooria.ms@gmail.com>"

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc libpq-dev build-essential python3-dev && \
    rm -rf /var/lib/apt/lists/*

ARG INSTALL_PATH
ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_PYTHON_DOWNLOADS=never
WORKDIR ${INSTALL_PATH}

# Install dependencies first (cached layer), then the project itself.
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-install-project --no-dev
COPY . .
RUN uv sync --frozen --no-dev

# stage 2: runtime
FROM ${python}

RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 wget && \
    rm -rf /var/lib/apt/lists/*

RUN adduser --disabled-login worker
ARG INSTALL_PATH
WORKDIR ${INSTALL_PATH}

COPY --from=builder --chown=worker:worker ${INSTALL_PATH} ${INSTALL_PATH}
# Put the uv-managed virtualenv on PATH so `rankr` is directly runnable.
ENV PATH="${INSTALL_PATH}/.venv/bin:$PATH"

USER worker
