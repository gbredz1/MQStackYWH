# syntax=docker/dockerfile:1

FROM python:3.11-alpine
RUN apk add --no-cache gcc musl-dev linux-headers
RUN pip install poetry==1.8.3

WORKDIR /app
COPY src .
COPY pyproject.toml .
RUN poetry install --only main
COPY tests tests

ENV APP=worker.py
ENV LOG_LEVEL=INFO

CMD poetry run python ${APP}