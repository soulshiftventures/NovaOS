FROM python:3.11-slim

WORKDIR /app

COPY main.py /app/main.py

RUN pip install --upgrade pip \
    && pip install --no-cache-dir redis openai

ENTRYPOINT ["python", "/app/main.py"]

