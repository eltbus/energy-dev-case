FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt ./
COPY ./src/main/ ./main
RUN pip install -r requirements.txt --no-cache-dir
CMD ["python", "-m", "uvicorn", "main.entrypoint:api", "--host", "0.0.0.0"]
