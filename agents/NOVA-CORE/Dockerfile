FROM python:3.11-slim

# Work from repo root
WORKDIR /app

# Copy everything into the image
COPY . .

# Install exactly what NOVA-CORE needs
RUN pip install --upgrade pip \
    && pip install --no-cache-dir redis openai

# Run your NOVA-CORE loop
CMD ["python", "agents/NOVA-CORE/nova.py"]
