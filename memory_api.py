# memory_api.py
# NovaOS Memory API: root welcome, health check, and Postgres-backed search.

import os
from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import JSONResponse
import psycopg
from psycopg.rows import dict_row

app = FastAPI(title="NovaOS Memory API")

def _db_url() -> str:
    db = (os.getenv("DATABASE_URL") or "").strip()
    if not db:
        raise RuntimeError("DATABASE_URL is not set")
    # Enforce TLS on hosted DBs if not present
    if "sslmode=" not in db:
        db += ("?sslmode=require" if "?" not in db else "&sslmode=require")
    return db

@app.get("/")
def root():
    return {
        "status": "online",
        "service": "NovaOS Memory API",
        "endpoints": ["/health", "/search?query=...&limit=5"]
    }

@app.get("/health")
def health():
    try:
        with psycopg.connect(_db_url()) as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT 1;")
        return {"ok": True}
    except Exception as e:
        return JSONResponse(status_code=503, content={"ok": False, "error": str(e)})

@app.get("/search")
def search(query: str = Query(...), limit: int = 5):
    if not (1 <= limit <= 50):
        raise HTTPException(400, "limit must be between 1 and 50")

    sql = """
        SELECT
            doc_id,
            chunk_id,
            LEFT(content, 300) AS snippet,
            ts_rank_cd(
              to_tsvector('english', content),
              plainto_tsquery('english', %s)
            ) AS score
        FROM memory_chunks
        WHERE to_tsvector('english', content) @@ plainto_tsquery('english', %s)
        ORDER BY score DESC
        LIMIT %s;
    """
    try:
        with psycopg.connect(_db_url(), row_factory=dict_row) as conn:
            with conn.cursor() as cur:
                cur.execute(sql, (query, query, limit))
                rows = cur.fetchall()
        return {"query": query, "count": len(rows), "results": rows}
    except Exception as e:
        raise HTTPException(500, str(e))
