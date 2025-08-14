# mcp/memory_server/memory_api.py
"""
NovaOS Memory API with Supabase (if available) and Postgres fallback.

- `/`       : simple service check with version hash.
- `/debug`  : shows whether SUPABASE_URL and SUPABASE_KEY are set and whether the Supabase client was initialized.
- `/messages`: returns messages from Supabase if available, otherwise falls back to Postgres.
- `/db/ping`: tests connection to DATABASE_URL.

Environment variables expected:
- SUPABASE_URL
- SUPABASE_KEY or SUPABASE_ANON_KEY (either one)
- DATABASE_URL (for Postgres fallback)
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
from datetime import datetime
import os
import psycopg

# Attempt to import Supabase client
try:
    from supabase import create_client, Client  # type: ignore
except ImportError:
    create_client = None
    Client = None  # type: ignore

app = FastAPI(title="NovaOS Memory API")

def _git_sha() -> str:
    return os.getenv("RENDER_GIT_COMMIT", os.getenv("GIT_SHA", "dev"))

# Read environment variables
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY") or os.getenv("SUPABASE_ANON_KEY")
DATABASE_URL = os.getenv("DATABASE_URL")

# Initialize Supabase client if possible
supabase_client: "Client | None" = None
if SUPABASE_URL and SUPABASE_KEY and create_client:
    try:
        supabase_client = create_client(SUPABASE_URL, SUPABASE_KEY)
        # simple sanity check: list tables (may fail silently)
        supabase_client.table("messages").select("id").limit(1).execute()
    except Exception as e:
        print(f"Supabase client initialization error: {e}")
        supabase_client = None

class Message(BaseModel):
    content: str

@app.get("/")
def root():
    return {"status": "online", "service": "novaos-memory", "version": _git_sha()}

@app.get("/debug")
def debug():
    """
    Diagnostic endpoint to check environment variables and Supabase client status.
    """
    return {
        "supabase_url_set": bool(SUPABASE_URL),
        "supabase_key_set": bool(SUPABASE_KEY),
        "supabase_client_initialized": supabase_client is not None,
        "database_url_set": bool(DATABASE_URL),
    }

@app.get("/db/ping")
def db_ping():
    """
    Check connectivity to a Postgres database defined by DATABASE_URL.
    """
    if not DATABASE_URL:
        return {"ok": False, "error": "DATABASE_URL not set"}
    dsn = DATABASE_URL
    if "sslmode=" not in dsn:
        dsn = dsn + ("&" if "?" in dsn else "?") + "sslmode=require"
    try:
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
    Store a message in Supabase if configured; otherwise use Postgres.
    """
    # Try Supabase
    if supabase_client:
        try:
            data = {"content": msg.content, "timestamp": datetime.utcnow().isoformat()}
            result = supabase_client.table("messages").insert(data).execute()
            return {"ok": True, "id": result.data[0]["id"]}
        except Exception as e:
            print(f"Supabase write failed: {e}")
            # fall through to Postgres

    # Fallback to Postgres
    if DATABASE_URL:
        dsn = DATABASE_URL
        if "sslmode=" not in dsn:
            dsn = dsn + ("&" if "?" in dsn else "?") + "sslmode=require"
        try:
            with psycopg.connect(dsn) as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        "CREATE TABLE IF NOT EXISTS messages (id SERIAL PRIMARY KEY, content TEXT NOT NULL, timestamp TIMESTAMPTZ NOT NULL);"
                    )
                    cur.execute(
                        "INSERT INTO messages (content, timestamp) VALUES (%s, %s) RETURNING id",
                        (msg.content, datetime.utcnow()),
                    )
                    new_id = cur.fetchone()[0]
                    conn.commit()
                return {"ok": True, "id": new_id}
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Postgres write failed: {e}")

    raise HTTPException(status_code=500, detail="No configured data store")

@app.get("/messages", response_model=List[Message])
def get_messages(limit: int = 100) -> List[Message]:
    """
    Retrieve the latest messages. Uses Supabase if available; otherwise Postgres.
    """
    # Try Supabase
    if supabase_client:
        try:
            response = (
                supabase_client.table("messages")
                .select("content")
                .order("timestamp", desc=True)
                .limit(limit)
                .execute()
            )
            rows = response.data or []
            return [Message(content=row["content"]) for row in rows]
        except Exception as e:
            print(f"Supabase read failed: {e}")
            # fall through to Postgres

    # Fallback to Postgres
    if DATABASE_URL:
        dsn = DATABASE_URL
        if "sslmode=" not in dsn:
            dsn = dsn + ("&" if "?" in dsn else "?") + "sslmode=require"
        try:
            with psycopg.connect(dsn) as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        "CREATE TABLE IF NOT EXISTS messages (id SERIAL PRIMARY KEY, content TEXT NOT NULL, timestamp TIMESTAMPTZ NOT NULL);"
                    )
                    cur.execute(
                        "SELECT content FROM messages ORDER BY timestamp DESC LIMIT %s",
                        (limit,),
                    )
                    rows = cur.fetchall()
            return [Message(content=row[0]) for row in rows]
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Postgres read failed: {e}")

    raise HTTPException(status_code=500, detail="No configured data store")
