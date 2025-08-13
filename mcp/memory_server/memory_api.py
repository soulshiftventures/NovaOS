# mcp/memory_server/memory_api.py
from fastapi import FastAPI
import os
import psycopg

app = FastAPI(title="NovaOS Memory API")

def _git_sha() -> str:
    # Prefer Render-provided commit envs if present
    return os.getenv("RENDER_GIT_COMMIT", os.getenv("GIT_SHA", "dev"))

@app.get("/")
def root():
    return {"status": "online", "service": "novaos-memory", "version": _git_sha()}

# Render health check (you configured /healthz)
@app.get("/healthz")
def healthz():
    return {"ok": True}

@app.get("/db/ping")
def db_ping():
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
