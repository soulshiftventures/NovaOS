FROM python:3.11-slim

# 1. Make NOVA-CORE the working dir
WORKDIR /app/agents/NOVA-CORE

# 2. Copy ONLY the NOVA-CORE agent
COPY agents/NOVA-CORE ./

# 3. Install dependencies
RUN pip install --upgrade pip \
    && pip install --no-cache-dir redis openai

# 4. Run nova.py directly
CMD ["python", "nova.py"]
