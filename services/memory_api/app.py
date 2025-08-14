# services/memory_api/app.py
"""
NovaOS Memory API

This FastAPI application stores and retrieves chat messages in a Supabase
table called "messages". It assumes SUPABASE_URL and SUPABASE_ANON_KEY are
set in the environment. If those variables are missing, the service will
still run but the /messages endpoints will return errors.
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
import os
from datetime import datetime

# Attempt to import Supabase client
try:
    from supabase import create_client, Client  # type: ignore
except ImportError:
    create_client = None
    Client = None  # type: ignore

app = FastAPI(title="NovaOS Memory API")

# Load Supabase credentials from environment
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_ANON_KEY = os.getenv("SUPABASE_ANON_KEY")

supabase: "Client | None" = None
if SUPABASE_URL and SUPABASE_ANON_KEY and create_client:
    try:
        supabase = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)
    except Exception:
        supabase = None

class Message(BaseModel):
    content: str

@app.get("/")
def root() -> dict[str, str]:
    """Health check root endpoint."""
    return {
        "status": "online",
        "service": "novaos-memory",
        "version": "0.3.0",
    }

@app.get("/health")
def health() -> dict[str, bool]:
    """Simple health endpoint."""
    return {"ok": True}

@app.post("/messages")
def add_message(msg: Message) -> dict[str, str]:
    """
    Store a message in the Supabase 'messages' table.
    Expects a JSON body like {"content": "your text"}.
    """
    if not supabase:
        raise HTTPException(status_code=500, detail="Supabase not configured")
    data = {
        "content": msg.content,
        "timestamp": datetime.utcnow().isoformat(),
    }
    result = supabase.table("messages").insert(data).execute()
    if result.data is None:
        raise HTTPException(status_code=500, detail="Failed to insert")
    return {"ok": True, "id": result.data[0]["id"]}

@app.get("/messages", response_model=List[Message])
def get_messages(limit: int = 100) -> List[Message]:
    """
    Retrieve the latest messages from Supabase.
    The limit parameter controls how many messages are returned.
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
