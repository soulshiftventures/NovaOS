FROM python:3.11-slim

WORKDIR /app

# Install base deps for dashboard + supervisor + agent needs
COPY services/novaos_dashboard/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy the health server + supervisor config
COPY services/novaos_dashboard/health.py ./health.py
COPY services/novaos_dashboard/supervisord.conf /etc/supervisor/conf.d/supervisord.conf

# Copy the Perplexity agent code into the image
COPY agents/PerplexityFetcherAgent /app/agents/PerplexityFetcherAgent

# Optional: install agent-specific requirements if you keep a file there
# RUN if [ -f agents/PerplexityFetcherAgent/requirements.txt ]; then pip install -r agents/PerplexityFetcherAgent/requirements.txt; fi

EXPOSE 8080
CMD ["supervisord", "-c", "/etc/supervisor/conf.d/supervisord.conf"]
