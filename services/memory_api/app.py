# services/memory_api/app.py
"""
NovaOS Memory API

This FastAPI application acts as the interface to the NovaOS memory store.
It reads configuration values from environment variables and can optionally
connect to a Supabase backend when SUPABASE_URL and SUPABASE_ANON_KEY
are present. Additional endpoints can be added later to read and write
chat history or other memory structures.
"""

from fastapi import FastAPI
import os

# Try to import the Supabase client if available
try:
    from supabase import create_client, Client  # type: ignore
except ImportError:
    create_client = None
    Client = None  # type: ignore

app = FastAPI(title="NovaOS Memory API")

# Load configuration from environment
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_ANON_KEY = os.getenv("SUPABASE_ANON_KEY")

supabase_client: "Client | None" = None
if SUPABASE_URL and SUPABASE_ANON_KEY and create_client:
    try:
        supabase_client = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)
    except Exception:
        # If client creation fails, leave supabase_client as None
        supabase_client = None

@app.get("/")
def root() -> dict[str, str]:
    """
    Root endpoint to confirm the service is running.
    """
    return {
        "status": "online",
        "service": "novaos-memory",
        "version": "0.2.0",
    }

@app.get("/health")
def health() -> dict[str, bool]:
    """
    Simple health endpoint returning {"ok": True}.
    """
    return {"ok": True}

@app.get("/db_health")
def db_health() -> dict[str, bool]:
    """
    Placeholder endpoint for database health checks.
    It always returns ok=True. You can extend this to
    check your Supabase or Postgres connection.
    """
    return {"ok": True}
