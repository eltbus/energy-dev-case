# syntax=docker/dockerfile:1

# Stage 1: Base image
FROM python:3.11-slim AS base
ARG UID=10001
ARG USER_NAME=appuser
RUN adduser \
    --disabled-password \
    --gecos "" \
    --home "/app" \
    --shell "/sbin/nologin" \
    --no-create-home \
    --uid "${UID}" \
    "${USER_NAME}"
WORKDIR /app
RUN chown ${USER_NAME}:${USER_NAME} /app
RUN --mount=type=cache,target=/root/.cache/pip \
    --mount=type=bind,source=requirements.txt,target=requirements.txt \
    python -m pip install -r requirements.txt

# Stage 2: Unittest stage
FROM base as unittest
RUN --mount=type=cache,target=/root/.cache/pip \
    --mount=type=bind,source=requirements-test.txt,target=requirements-test.txt \
    python -m pip install -r requirements-test.txt
COPY --chown=${USER_NAME}:${USER_NAME} ./src/main/ ./main
COPY ./src/tests/ ./tests
RUN PYTHONPATH=/app pytest -s -vvv /app/tests/unit

# Stage 3: Final stage
FROM base as final
COPY --from=unittest /app/main ./main
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
USER ${USER_NAME}
CMD ["python", "-m", "uvicorn", "main.entrypoint:api", "--host", "0.0.0.0"]
