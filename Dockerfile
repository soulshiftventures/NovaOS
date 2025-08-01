FROM python:3.11-slim

WORKDIR /app/agents/NOVA-CORE

# Copy the NOVA-CORE folder into the image
COPY agents/NOVA-CORE /app/agents/NOVA-CORE

# Ensure all dependencies (if any) are satisfied
RUN pip install --upgrade pip \
    && pip install --no-cache-dir redis openai

# Expose nothing (background worker)

CMD ["python", "nova.py"]


# NovaOS entrypoint
COPY main.py /app/main.py
ENTRYPOINT ["python", "/app/main.py"]
