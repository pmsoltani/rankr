ARG python=python:3.8-slim-buster

# stage 1: compile
FROM ${python} AS backend-compile

LABEL maintainer="Pooria Soltani <pooria.ms@gmail.com>"

RUN apt-get update && apt-get upgrade -y && \
    apt-get install -y gcc libpq-dev build-essential python3-dev && \
    apt-get clean

ARG INSTALL_PATH
ENV VIRTUAL_ENV=/opt/venv
WORKDIR ${INSTALL_PATH}

RUN python -m venv ${VIRTUAL_ENV}
# Entering venv:
ENV PATH="${VIRTUAL_ENV}/bin:$PATH"

ARG POETRY_VERSION
RUN pip install "poetry==${POETRY_VERSION}"

COPY pyproject.toml poetry.lock ./
RUN poetry install --no-interaction --no-ansi

# stage 2: build
FROM ${python}

RUN apt-get update && apt-get upgrade -y && \
    apt-get install -y libpq-dev && \
    apt-get clean

RUN adduser --disabled-login worker
ARG INSTALL_PATH
ENV VIRTUAL_ENV=/opt/venv
WORKDIR ${INSTALL_PATH}

# Entering venv:
ENV PATH="${VIRTUAL_ENV}/bin:$PATH"

COPY --from=backend-compile ${VIRTUAL_ENV} ${VIRTUAL_ENV}
COPY --chown=worker:worker . .
RUN poetry install --no-interaction --no-ansi
