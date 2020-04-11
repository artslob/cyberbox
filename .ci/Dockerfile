FROM python:3.7.4-buster

ENV CI_POETRY_URL="https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py" \
    PATH="/root/.poetry/bin:${PATH}" \
    PYTHONFAULTHANDLER=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONHASHSEED=random \
    PIP_NO_CACHE_DIR=off \
#    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PIP_DEFAULT_TIMEOUT=100 \
    POETRY_VERSION=1.0.5

RUN curl -sSL "$CI_POETRY_URL" | python

RUN poetry config virtualenvs.create false

WORKDIR /ci-image

COPY poetry.lock pyproject.toml ./

RUN    poetry install \
    && poetry show
