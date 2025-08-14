# mcp/memory_server/memory_api.py
"""
NovaOS Memory API using Postgres

This FastAPI application stores and retrieves chat messages in a Postgres
table called "messages". It also keeps the original health and DB ping
endpoints for backwards compatibility.

Environment variables required:
- DATABASE_URL (connection string for Postgres)
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
from datetime import datetime
import os
import psycopg

app = FastAPI(title="NovaOS Memory API")

def _git_sha() -> str:
    # Prefer Render-provided commit envs if present
    return os.getenv("RENDER_GIT_COMMIT", os.getenv("GIT_SHA", "dev"))

# Postgres DSN
DB_DSN = os.getenv("DATABASE_URL", "").strip()

def init_db() -> None:
    """
    Create the messages table if it does not exist.
    """
    if not DB_DSN:
        return
    dsn = DB_DSN
    # enforce SSL in hosted envs
    if "sslmode=" not in dsn:
        dsn = dsn + ("&" if "?" in dsn else "?") + "sslmode=require"
    try:
        with psycopg.connect(dsn) as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    CREATE TABLE IF NOT EXISTS messages (
                        id SERIAL PRIMARY KEY,
                        content TEXT NOT NULL,
                        timestamp TIMESTAMPTZ NOT NULL
                    )
                    """
                )
                conn.commit()
    except Exception as e:
        # Log errors during table creation; the /messages endpoints will
        # surface DB errors on use.
        print("init_db error:", e)

# Initialise DB on startup
init_db()

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
    if not DB_DSN:
        return {"ok": False, "error": "DATABASE_URL not set"}
    try:
        dsn = DB_DSN
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
    Store a message in the Postgres 'messages' table.
    Expects JSON body: {"content": "<text>"}.
    """
    if not DB_DSN:
        raise HTTPException(status_code=500, detail="DATABASE_URL not configured")
    dsn = DB_DSN
    if "sslmode=" not in dsn:
        dsn = dsn + ("&" if "?" in dsn else "?") + "sslmode=require"
    try:
        with psycopg.connect(dsn) as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "INSERT INTO messages (content, timestamp) VALUES (%s, %s) RETURNING id",
                    (msg.content, datetime.utcnow()),
                )
                new_id = cur.fetchone()[0]
                conn.commit()
        return {"ok": True, "id": new_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/messages", response_model=List[Message])
def get_messages(limit: int = 100) -> List[Message]:
    """
    Retrieve the latest messages from Postgres.
    Use the 'limit' query parameter to limit the number of returned messages.
    """
    if not DB_DSN:
        raise HTTPException(status_code=500, detail="DATABASE_URL not configured")
    dsn = DB_DSN
    if "sslmode=" not in dsn:
        dsn = dsn + ("&" if "?" in dsn else "?") + "sslmode=require"
    try:
        with psycopg.connect(dsn) as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT content FROM messages ORDER BY timestamp DESC LIMIT %s",
                    (limit,),
                )
                rows = cur.fetchall()
        return [Message(content=row[0]) for row in rows]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
