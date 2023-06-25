# syntax=docker/dockerfile:1

# Environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Stage 1: Base image
FROM python:3.11-slim AS base
WORKDIR /app
COPY requirements.txt ./
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install -r requirements.txt

# Stage 2: Unittest stage
FROM base as unittest
COPY requirements-dev.txt ./
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install -r requirements-dev.txt
COPY ./src/main/ ./main
COPY ./src/tests/ ./tests
RUN PYTHONPATH=/app pytest -s -vvv /app/tests/unit

# Stage 3: Final stage
FROM base as final
COPY --from=unittest /app/main ./main
CMD ["python", "-m", "uvicorn", "main.entrypoint:api", "--host", "0.0.0.0"]
