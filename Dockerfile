syntax=docker/dockerfile:1

FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt ./
RUN pip install -r requirements.txt --no-cache-dir
COPY ./src/main/ ./main
CMD ["python", "-m", "uvicorn", "main.entrypoint:api", "--host", "0.0.0.0"]
