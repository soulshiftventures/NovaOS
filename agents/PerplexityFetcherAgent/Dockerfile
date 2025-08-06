FROM python:3.11-slim

WORKDIR /app

COPY main.py ./

RUN ls -l /app && pip install --no-cache-dir redis requests python-dotenv

CMD ["python3", "main.py"]
