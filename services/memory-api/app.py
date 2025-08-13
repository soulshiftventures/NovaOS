import os, json, hashlib
from typing import List, Optional
import psycopg
from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel
from openai import OpenAI

DB_URL = os.environ.get("DATABASE_URL")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
EMBED_MODEL = "text-embedding-3-small"  # 1536 dims

if not DB_URL:
    raise RuntimeError("DATABASE_URL not set")
if not OPENAI_API_KEY:
    raise RuntimeError("OPENAI_API_KEY not set")

client = OpenAI(api_key=OPENAI_API_KEY)
app = FastAPI(title="NovaOS Memory API")

def vec_str(v: List[float]) -> str:
    return "[" + ",".join(f"{x:.6f}" for x in v) + "]"

def embed_text(text: str) -> List[float]:
    r = client.embeddings.create(model=EMBED_MODEL, input=text)
    return r.data[0].embedding

def conn():
    return psycopg.connect(DB_URL)

class UpsertReq(BaseModel):
    source: str
    doc_id: str
    chunk_id: Optional[str] = None
    content: str
    metadata: Optional[dict] = None

@app.get("/health")
def health():
    return {"ok": True}

@app.post("/upsert")
def upsert(r: UpsertReq):
    chunk_id = r.chunk_id or hashlib.sha1(r.content.encode("utf-8")).hexdigest()[:16]
    emb = embed_text(r.content)
    with conn() as c, c.cursor() as cur:
        cur.execute("""
            INSERT INTO memory_chunks (source, doc_id, chunk_id, content, embedding, metadata)
            VALUES (%s, %s, %s, %s, %s::vector, %s::jsonb)
            ON CONFLICT (source, doc_id, chunk_id) DO UPDATE
              SET content=EXCLUDED.content,
                  embedding=EXCLUDED.embedding,
                  metadata=COALESCE(EXCLUDED.metadata, '{}'::jsonb);
        """, (r.source, r.doc_id, chunk_id, r.content, vec_str(emb), json.dumps(r.metadata or {})))
    return {"status":"ok","source":r.source,"doc_id":r.doc_id,"chunk_id":chunk_id}

@app.get("/search")
def search(q: str = Query(..., min_length=2), k: int = 8):
    q_emb = vec_str(embed_text(q))
    with conn() as c, c.cursor() as cur:
        cur.execute("""
            SELECT content, metadata, source, doc_id, chunk_id, (embedding <-> %s::vector) AS dist
            FROM memory_chunks
            ORDER BY embedding <-> %s::vector
            LIMIT %s;
        """, (q_emb, q_emb, k))
        rows = cur.fetchall()
    return [
        {"content": content, "metadata": metadata, "source": source,
         "doc_id": doc_id, "chunk_id": chunk_id, "score": float(dist)}
        for (content, metadata, source, doc_id, chunk_id, dist) in rows
    ]
