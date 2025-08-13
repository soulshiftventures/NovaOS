FROM python:3.11-slim

WORKDIR /app

COPY main.py /app/

RUN pip install --no-cache-dir redis requests python-dotenv

CMD ["python3", "main.py"]
