FROM python:3.7.4-buster

ENV CI_POETRY_URL="https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py" \
    PATH="/root/.poetry/bin:${PATH}" \
    PYTHONFAULTHANDLER=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=off \
    PIP_DEFAULT_TIMEOUT=100 \
    POETRY_VERSION=1.0.5

RUN curl -sSL "$CI_POETRY_URL" | python

RUN poetry config virtualenvs.create false

WORKDIR /cyberbox

COPY poetry.lock pyproject.toml ./

RUN    poetry install \
    && poetry show

EXPOSE 8000

RUN mkdir -p /cyberbox-files

COPY . .

RUN poetry install

CMD ["uvicorn", "cyberbox.asgi:app", "--host", "0.0.0.0", "--reload"]
