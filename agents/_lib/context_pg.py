import os
import json
from typing import List, Dict, Any
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse
import psycopg

# --- DB helpers --------------------------------------------------------------

def _with_sslmode(db_url: str) -> str:
    parsed = urlparse(db_url.strip())
    q = parse_qs(parsed.query)
    if "sslmode" not in q:
        q["sslmode"] = ["require"]
    return urlunparse((
        parsed.scheme, parsed.netloc, parsed.path, parsed.params,
        urlencode(q, doseq=True), parsed.fragment
    ))

def _conn():
    db = os.environ["DATABASE_URL"]
    return psycopg.connect(_with_sslmode(db))

# --- Public API --------------------------------------------------------------

def learn(doc_id: str, content: str, tags: List[str] | None = None) -> Dict[str, Any]:
    """
    Upsert a single-note document into memory_chunks.
    - source: 'dashboard'
    - doc_id: your title (stable identifier)
    - chunk_id: '0' (one chunk per note)
    """
    if not doc_id or not content:
        raise ValueError("doc_id and content are required")

    meta = {"tags": tags or []}
    with _conn() as c:
        with c.cursor() as cur:
            cur.execute(
                """
                INSERT INTO memory_chunks (source, doc_id, chunk_id, content, metadata)
                VALUES (%s, %s, %s, %s, %s::jsonb)
                ON CONFLICT (source, doc_id, chunk_id)
                DO UPDATE SET content = EXCLUDED.content, metadata = EXCLUDED.metadata
                RETURNING xmax::text; -- '0' on insert, else nonzero on update
                """,
                ("dashboard", doc_id, "0", content, json.dumps(meta))
            )
            updated = cur.fetchone()[0] != "0"
    return {"status": "updated" if updated else "ok", "doc_id": doc_id}

def fetch_context(query: str, k: int = 8) -> List[Dict[str, Any]]:
    """
    Title-aware + content-aware search.
    - Matches if doc_id equals, doc_id ILIKE, or content full-text matches.
    - Ranks: exact title >> partial title >> content match.
    """
    if not query:
        return []

    q_ilike = f"%{query}%"
    rows: List[Dict[str, Any]] = []

    sql = """
    WITH scored AS (
      SELECT
        doc_id,
        chunk_id,
        content,
        /* Content rank (0 if no FTS match) */
        COALESCE(ts_rank_cd(to_tsvector('english', content),
                            plainto_tsquery('english', %s)), 0) AS content_rank,
        /* Title boosts */
        CASE
          WHEN doc_id = %s THEN 10.0
          WHEN doc_id ILIKE %s THEN 5.0
          ELSE 0.0
        END AS title_boost
      FROM memory_chunks
      WHERE
        doc_id = %s
        OR doc_id ILIKE %s
        OR to_tsvector('english', content) @@ plainto_tsquery('english', %s)
    )
    SELECT
      doc_id,
      chunk_id,
      content,
      (content_rank + title_boost) AS score
    FROM scored
    ORDER BY score DESC
    LIMIT %s;
    """

    params = (query, query, q_ilike, query, q_ilike, query, k)

    with _conn() as c, c.cursor() as cur:
        cur.execute(sql, params)
        for doc_id, chunk_id, content, score in cur.fetchall():
            rows.append({
                "doc_id": doc_id,
                "chunk_id": chunk_id,
                "content": content,
                "score": float(score),
            })
    return rows
