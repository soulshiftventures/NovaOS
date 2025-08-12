import os
import json
import re
from pathlib import Path
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse

import psycopg


# ---------- helpers ----------

def ensure_ssl_require(db_url: str) -> str:
    db_url = db_url.strip().replace("\n", "").replace("\r", "")
    if "sslmode=" not in db_url:
        db_url += ("?sslmode=require" if "?" not in db_url else "&sslmode=require")
    return db_url

SECRET_PATTERNS = [
    re.compile(r"sk-[A-Za-z0-9]{20,}"),                     # OpenAI-like
    re.compile(r"(?i)api[_-]?key[:=]\s*[A-Za-z0-9-_]{16,}"),
    re.compile(r"[A-Za-z0-9_\-]{24,}\.[A-Za-z0-9_\-]{10,}"),  # JWT-ish
    re.compile(r"[A-Fa-f0-9]{32,}"),                        # long hex
]

def redact(text: str) -> str:
    redacted = text
    for pat in SECRET_PATTERNS:
        redacted = pat.sub("[REDACTED]", redacted)
    return redacted

def chunk_text(text: str, chunk_size: int = 3000, overlap: int = 300):
    chunks = []
    start = 0
    L = len(text)
    if L == 0:
        return []
    while start < L:
        end = min(start + chunk_size, L)
        chunks.append(text[start:end])
        if end == L:
            break
        start = max(0, end - overlap)
    return chunks

def slugify(s: str) -> str:
    s = re.sub(r"[^a-zA-Z0-9]+", "-", s.strip().lower()).strip("-")
    return s or "untitled"

# ---------- parsing ChatGPT export ----------

def is_single_file_export(path: Path) -> bool:
    # Typical single-file export name
    return path.name == "conversations.json"

def load_conversation_objs(base: Path):
    """
    Yields dicts for each conversation from either:
    - a single conversations.json file, or
    - a folder containing many JSON files (one per conversation)
    """
    if base.is_file() and is_single_file_export(base):
        data = json.loads(base.read_text(encoding="utf-8"))
        # Expecting a list
        for obj in data:
            yield obj
        return

    # Otherwise treat as a directory of JSON files
    if base.is_dir():
        for p in sorted(base.glob("*.json")):
            try:
                obj = json.loads(p.read_text(encoding="utf-8"))
            except Exception:
                continue
            # Some exports store a dict per file; pass through
            yield obj

def extract_messages_from_mapping(mapping: dict):
    """
    Newer ChatGPT exports store messages inside a mapping: { id: {message: {...}} }.
    We flatten by create_time (when present), otherwise keep insertion order.
    Return list of (role, text).
    """
    msgs = []
    for node_id, node in mapping.items():
        msg = node.get("message")
        if not msg:
            continue
        author = (msg.get("author") or {}).get("role") or "unknown"
        content = msg.get("content") or {}
        parts = content.get("parts") or []
        text = "\n".join(str(p) for p in parts if isinstance(p, (str, int, float)))
        if text.strip():
            msgs.append({
                "role": author,
                "text": text,
                "ts": msg.get("create_time") or 0.0,
            })
    # sort by timestamp if available
    msgs.sort(key=lambda m: (m["ts"] if isinstance(m["ts"], (int, float)) else 0.0))
    return [(m["role"], m["text"]) for m in msgs]

def conversation_to_text(conv: dict) -> tuple[str, str]:
    """
    Returns (doc_id, full_text)
    Tries to use conv['id'] + title when available.
    """
    title = conv.get("title") or "Untitled"
    cid = conv.get("id") or ""
    header = f"# {title}\n"
    body_lines = []

    if "mapping" in conv and isinstance(conv["mapping"], dict):
        pairs = extract_messages_from_mapping(conv["mapping"])
    else:
        # Fallback older format: conv.get("messages", [])
        pairs = []
        for m in conv.get("messages", []):
            role = (m.get("author") or {}).get("role") or m.get("role") or "unknown"
            content = m.get("content") or {}
            parts = content.get("parts") or []
            text = "\n".join(str(p) for p in parts if isinstance(p, (str, int, float)))
            if text.strip():
                pairs.append((role, text))

    for role, text in pairs:
        role_label = role.lower()
        if role_label not in ("system", "user", "assistant"):
            role_label = "user" if role_label == "tool" else role_label
        body_lines.append(f"**{role_label}:** {text}".strip())

    full_text = header + "\n\n" + "\n\n".join(body_lines)
    full_text = redact(full_text)

    base_id = slugify(title)
    if cid:
        doc_id = f"{base_id}-{slugify(cid)[:12]}"
    else:
        doc_id = base_id
    return doc_id, full_text

# ---------- DB upsert ----------

UPSERT_SQL = """
INSERT INTO memory_chunks (source, doc_id, chunk_id, content, metadata)
VALUES (%s, %s, %s, %s, %s::jsonb)
ON CONFLICT (source, doc_id, chunk_id)
DO UPDATE SET content = EXCLUDED.content, metadata = EXCLUDED.metadata;
"""

def upsert_conversation(conn, doc_id: str, text: str, meta: dict):
    chunks = chunk_text(text, 3000, 300)
    total = 0
    with conn.cursor() as cur:
        for i, chunk in enumerate(chunks):
            chunk_id = f"{doc_id}:{i}"
            cur.execute(UPSERT_SQL, ("chatgpt", doc_id, chunk_id, chunk, json.dumps(meta)))
            total += 1
    conn.commit()
    return total

# ---------- main ----------

def main():
    root = Path.cwd()
    export_dir = root / "brain" / "chatgpt_export"

    if not export_dir.exists():
        print("NO_EXPORT_DIR: brain/chatgpt_export not found")
        return

    db_url = os.environ.get("DATABASE_URL")
    if not db_url:
        raise RuntimeError("DATABASE_URL not set")
    db_url = ensure_ssl_require(db_url)

    total_convs = 0
    total_chunks = 0

    with psycopg.connect(db_url) as conn:
        # Support either a single file brain/chatgpt_export/conversations.json
        # or many JSON files inside brain/chatgpt_export/
        # If both exist, we'll ingest both.
        single_file = export_dir / "conversations.json"
        sources = []
        if single_file.exists():
            sources.append(single_file)
        # Also include any JSON files at the top level (skip conversations.json duplicate)
        other_jsons = [p for p in export_dir.glob("*.json") if p.name != "conversations.json"]
        if other_jsons:
            sources.append(export_dir)

        if not sources:
            print("NO_JSON_FOUND: put conversations.json or *.json files into brain/chatgpt_export/")
            return

        for src in sources:
            for conv in load_conversation_objs(src):
                try:
                    doc_id, full_text = conversation_to_text(conv)
                    meta = {
                        "title": conv.get("title"),
                        "source_path": str(src),
                        "export_kind": "single" if src.is_file() else "multi",
                    }
                    n = upsert_conversation(conn, doc_id, full_text, meta)
                    total_convs += 1
                    total_chunks += n
                except Exception as e:
                    print(f"SKIP_CONV: {e}")

    print(f"INGEST_DONE conversations={total_convs} chunks={total_chunks}")

if __name__ == "__main__":
    main()
