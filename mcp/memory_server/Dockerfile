# mcp/memory_server/Dockerfile
FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements.txt .
RUN python -m pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

COPY . .

# Render will inject $PORT and override CMD via the “Docker Command” setting,
# but we keep a sensible default for local runs:
CMD ["uvicorn", "memory_api:app", "--host", "0.0.0.0", "--port", "10000"]
