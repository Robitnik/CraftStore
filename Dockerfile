FROM python:3.12-slim

RUN pip install poetry

RUN mkdir -p /app/craftstore

WORKDIR /app/craftstore


COPY craftstore/pyproject.toml /app/craftstore/

RUN poetry install

EXPOSE 12500
