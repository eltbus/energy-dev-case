# syntax=docker/dockerfile:1

# Stage 1: Base image
FROM python:3.11-slim AS base
WORKDIR /app
RUN --mount=type=cache,target=/root/.cache/pip \
    --mount=type=bind,source=./requirements.txt,target=./requirements.txt \
    python -m pip install -r requirements.txt

# Stage 2: Unittest stage
FROM base as unittest
RUN --mount=type=cache,target=/root/.cache/pip \
    --mount=type=bind,source=./requirements-dev.txt,target=./requirements-dev.txt \
    python -m pip install -r requirements-dev.txt
COPY ./src/main/ ./main
COPY ./src/tests/ ./tests
RUN PYTHONPATH=/app pytest -s -vvv /app/tests/unit

# Stage 3: Final stage
FROM base as final
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
COPY --from=unittest /app/main ./main
CMD ["python", "-m", "uvicorn", "main.entrypoint:api", "--host", "0.0.0.0"]
