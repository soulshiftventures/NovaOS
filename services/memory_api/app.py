# services/memory_api/app.py
#!/usr/bin/env python3
"""
NovaOS Memory API - minimal app to satisfy health and root routes.
"""

from fastapi import FastAPI
import os
import psycopg

app = FastAPI(title="NovaOS Memory API")

@app.get("/")
def root():
    return {
        "status": "online",
        "service": "novaos-memory",
        "version": os.getenv("GIT_SHA", "dev")
    }

@app.get("/health")
def health():
    return {"ok": True}

@app.get("/db/ping")
def db_ping():
    dsn = os.getenv("DATABASE_URL", "")
    if not dsn:
        return {"ok": False, "error": "DATABASE_URL not set"}
    try:
        if "sslmode=" not in dsn:
            dsn = dsn + ("&" if "?" in dsn else "?") + "sslmode=require"
        with psycopg.connect(dsn) as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT 1")
                cur.fetchone()
        return {"ok": True}
    except Exception as e:
        return {"ok": False, "error": str(e)}
