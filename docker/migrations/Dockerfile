FROM python:3.9.5
RUN mkdir -p /usr/src/postgres_migrations/
WORKDIR /usr/src/postgres_migrations/


RUN apt-get update && \
    apt-get install -y --no-install-recommends dos2unix

RUN pip install --upgrade pip

RUN pip install poetry

COPY poetry.lock pyproject.toml poetry.toml /usr/src/postgres_migrations/

RUN poetry install --no-dev

COPY . /usr/src/postgres_migrations/

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1


RUN dos2unix scripts/*

