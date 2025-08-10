import os, json, psycopg
from typing import List, Dict, Any
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse

def _clean_url(u: str) -> str:
    return (u or "").strip().replace("\n","").replace("\r","")

def _add_sslmode(url: str) -> str:
    parsed = urlparse(url)
    q = parse_qs(parsed.query)
    if 'sslmode' not in q:
        q['sslmode'] = ['require']
    new_q = urlencode(q, doseq=True)
    return urlunparse((parsed.scheme, parsed.netloc, parsed.path, parsed.params, new_q, parsed.fragment))

def _conn():
    db = _add_sslmode(_clean_url(os.environ.get("DATABASE_URL", "")))
    if not db:
        raise RuntimeError("DATABASE_URL not set")
    return psycopg.connect(db)

def fetch_context(query: str, k: int = 8) -> List[Dict[str, Any]]:
    """
    Full-text search over memory_chunks. No embeddings required.
    Returns: [{content, metadata, source, doc_id, chunk_id, score}]
    """
    sql = """
    SELECT content, metadata, source, doc_id, chunk_id,
           ts_rank_cd(to_tsvector('english', content),
                      plainto_tsquery('english', %s)) AS rank
    FROM memory_chunks
    WHERE to_tsvector('english', content) @@ plainto_tsquery('english', %s)
    ORDER BY rank DESC
    LIMIT %s;
    """
    with _conn() as c, c.cursor() as cur:
        cur.execute(sql, (query, query, k))
        rows = cur.fetchall()
    if rows:
        return [
            {"content": ct, "metadata": md, "source": src,
             "doc_id": did, "chunk_id": cid, "score": float(rk)}
            for (ct, md, src, did, cid, rk) in rows
        ]
    # Fallback: substring search if FTS finds nothing
    with _conn() as c, c.cursor() as cur:
        cur.execute("""
            SELECT content, metadata, source, doc_id, chunk_id, 0.0 AS score
            FROM memory_chunks
            WHERE content ILIKE '%%' || %s || '%%'
            ORDER BY created_at DESC
            LIMIT %s;
        """, (query, k))
        rows = cur.fetchall()
    return [
        {"content": ct, "metadata": md, "source": src,
         "doc_id": did, "chunk_id": cid, "score": 0.0}
        for (ct, md, src, did, cid, _) in rows
    ]

def learn(title: str, body: str, tags=None) -> Dict[str, Any]:
    """
    Persist an event/summary into memory_chunks.
    """
    tags = tags or []
    doc_id = f"historian/{title.lower().replace(' ', '-')}"

    with _conn() as c, c.cursor() as cur:
        cur.execute(
            """
            INSERT INTO memory_chunks (source, doc_id, chunk_id, content, metadata)
            VALUES (%s, %s, %s, %s, %s::jsonb)
            ON CONFLICT (source, doc_id, chunk_id) DO UPDATE
              SET content = EXCLUDED.content,
                  metadata = EXCLUDED.metadata;
            """,
            ("historian", doc_id, doc_id, body, json.dumps({"tags": tags})),
        )
    return {"status": "ok", "doc_id": doc_id}
