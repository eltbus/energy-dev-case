# syntax=docker/dockerfile:1

FROM python:3.11-slim
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
WORKDIR /app
COPY requirements.txt ./
RUN pip install -r requirements.txt --no-cache-dir
COPY ./src/main/ ./main
CMD ["python", "-m", "uvicorn", "main.entrypoint:api", "--host", "0.0.0.0"]
