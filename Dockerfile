#syntax=docker/dockerfile:1
FROM python:3.11-slim-bookworm AS builder

RUN apt-get update \
    && apt-get install -y --no-install-recommends --allow-unauthenticated \
        build-essential \
        curl \
        vim \
    && rm -rf /var/cache/apt/* \
    && rm -rf /var/lib/apt/lists/*

ENV PYTHONUNBUFFERED=1 \
    PYTHONHASHSEED=random \
    PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    # Poetry's configuration:
    POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_IN_PROJECT=true \
    POETRY_CACHE_DIR="/var/cache/pypoetry" \
    POETRY_HOME="/usr/local" \
    POETRY_VERSION=1.8.0 \
    USER_HOME="/home/docbot" \
    PYTHONPATH=$USER_HOME

# install poetry - respects $POETRY_VERSION & $POETRY_HOME
RUN curl -sSL https://install.python-poetry.org | python3 -

WORKDIR $USER_HOME

COPY poetry.lock pyproject.toml README.md ./

# install runtime deps - uses $POETRY_VIRTUALENVS_IN_PROJECT internally
# install dependencies here so that it is cahed at docker layers
RUN --mount=type=cache,target=$POETRY_CACHE_DIR poetry install --only main --no-interaction --no-ansi --no-root

# The runtime image - only run the code in venv
FROM python:3.11-slim-bookworm AS runtime

# Env variable USER_HOME needs to be configured again because of multi-stage build
ENV USER_HOME="/home/docbot"
ENV VIRTUAL_ENV="$USER_HOME/.venv"
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

WORKDIR $USER_HOME

COPY --from=builder ${VIRTUAL_ENV} ${VIRTUAL_ENV}
COPY --from=builder $USER_HOME/poetry.lock $USER_HOME/pyproject.toml $USER_HOME/README.md ./
COPY src $USER_HOME/src
RUN pip install -e .

CMD  ["streamlit", "run", "src/docbot/fe/main.py", " --logger.level=info"]

EXPOSE 8501
