FROM python:3.11-slim
WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY server.py ./
# Render sets $PORT at runtime; use it, default to 8080 locally
EXPOSE 8080
CMD ["bash", "-lc", "uvicorn server:app --host 0.0.0.0 --port ${PORT:-8080}"]
