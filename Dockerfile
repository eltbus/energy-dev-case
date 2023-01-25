FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt ./
COPY ./main.py ./main.py
RUN pip install -r requirements.txt --no-cache-dir
CMD ["python", "-m", "uvicorn", "main:app", "--host", "0.0.0.0"]
