# mcp/memory_server/memory_api.py
"""
NovaOS Memory API using Supabase

This FastAPI application stores and retrieves chat messages in a Supabase
table called "messages". It also keeps the original health and DB ping
endpoints for backwards compatibility.

Environment variables required:
- SUPABASE_URL
- SUPABASE_KEY (preferred) or SUPABASE_ANON_KEY
- DATABASE_URL (optional, used only for /db/ping)
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
from datetime import datetime
import os
import psycopg  # only used by db_ping

# Try to import the Supabase client
try:
    from supabase import create_client, Client  # type: ignore
except ImportError:
    create_client = None
    Client = None  # type: ignore

app = FastAPI(title="NovaOS Memory API")

def _git_sha() -> str:
    # Prefer Render-provided commit envs if present
    return os.getenv("RENDER_GIT_COMMIT", os.getenv("GIT_SHA", "dev"))

# Configure Supabase client
# We support both SUPABASE_KEY and SUPABASE_ANON_KEY for backwards compatibility.
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY") or os.getenv("SUPABASE_ANON_KEY")

supabase: "Client | None" = None
if SUPABASE_URL and SUPABASE_KEY and create_client:
    try:
        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
    except Exception:
        # If the client fails to initialize (e.g. invalid key), leave supabase
        # unset so the /messages endpoints will return a helpful error.
        supabase = None

# Pydantic model for incoming messages
class Message(BaseModel):
    content: str

@app.get("/")
def root():
    return {"status": "online", "service": "novaos-memory", "version": _git_sha()}

@app.get("/healthz")
def healthz():
    return {"ok": True}

@app.get("/db/ping")
def db_ping():
    """
    Check connectivity to a Postgres database defined by DATABASE_URL.
    """
    dsn = os.getenv("DATABASE_URL", "").strip()
    if not dsn:
        return {"ok": False, "error": "DATABASE_URL not set"}
    try:
        # enforce SSL in hosted envs
        if "sslmode=" not in dsn:
            dsn = dsn + ("&" if "?" in dsn else "?") + "sslmode=require"
        with psycopg.connect(dsn) as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT 1")
                cur.fetchone()
        return {"ok": True}
    except Exception as e:
        return {"ok": False, "error": str(e)}

@app.post("/messages")
def add_message(msg: Message) -> dict[str, str]:
    """
    Store a message in the Supabase 'messages' table.
    Expects JSON body: {"content": "<text>"}.
    """
    if not supabase:
        raise HTTPException(status_code=500, detail="Supabase not configured")
    data = {
        "content": msg.content,
        "timestamp": datetime.utcnow().isoformat(),
    }
    result = supabase.table("messages").insert(data).execute()
    if not result.data:
        raise HTTPException(status_code=500, detail="Failed to insert")
    return {"ok": True, "id": result.data[0]["id"]}

@app.get("/messages", response_model=List[Message])
def get_messages(limit: int = 100) -> List[Message]:
    """
    Retrieve the latest messages from Supabase.
    Use the 'limit' query parameter to limit the number of returned messages.
    """
    if not supabase:
        raise HTTPException(status_code=500, detail="Supabase not configured")
    response = (
        supabase.table("messages")
        .select("content")
        .order("timestamp", desc=True)
        .limit(limit)
        .execute()
    )
    rows = response.data or []
    return [Message(content=row["content"]) for row in rows]
