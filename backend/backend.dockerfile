FROM python:3.7-alpine

LABEL maintainer="Pooria Soltani <pooria.ms@gmail.com>"

RUN adduser -D worker

RUN apk add --no-cache postgresql-libs && \
    apk add --no-cache --virtual .build-deps \
    gcc libffi-dev musl-dev postgresql-dev build-base

ARG POETRY_VERSION
RUN pip install "poetry==${POETRY_VERSION}"

ARG INSTALL_PATH
WORKDIR ${INSTALL_PATH}
COPY poetry.lock pyproject.toml ./

RUN poetry config virtualenvs.create false && \
    poetry install --no-interaction --no-ansi

ENV PATH="/home/worker/.local/bin:${PATH}"

COPY --chown=worker:worker . .
RUN poetry install --no-interaction --no-ansi

USER worker
