# Minimal, reliable Python base
FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

# Workdir
WORKDIR /app

# System deps (slim works fine for psycopg[binary], so no build tools needed)

# Install Python deps first (better layer cache)
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy the app
COPY . .

# Streamlit runtime env
ENV STREAMLIT_SERVER_HEADLESS=true
ENV STREAMLIT_BROWSER_GATHER_USAGE_STATS=false

# Render provides $PORT. Use shell so $PORT expands.
CMD bash -lc 'streamlit run main.py --server.port "$PORT" --server.address 0.0.0.0 --server.headless true'
