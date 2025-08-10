import os, json, psycopg
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse

def add_sslmode(url: str) -> str:
    parsed = urlparse(url)
    q = parse_qs(parsed.query)
    if 'sslmode' not in q:
        q['sslmode'] = ['require']
    new_q = urlencode(q, doseq=True)
    return urlunparse((parsed.scheme, parsed.netloc, parsed.path, parsed.params, new_q, parsed.fragment))

def table_exists(conn, table_name: str) -> bool:
    with conn.cursor() as cur:
        cur.execute("SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = %s);", (table_name,))
        return bool(cur.fetchone()[0])

def chunk_text(text: str, chunk_size: int = 3000, overlap: int = 300):
    chunks = []
    start = 0
    n = len(text)
    while start < n:
        end = min(n, start + chunk_size)
        chunks.append(text[start:end])
        start = end - overlap if end - overlap > start else end
    return chunks

def upsert_chunk(conn, rel_path: str, idx: int, chunk: str):
    chunk_id = f"{rel_path}:{idx}"
    metadata = {"path": rel_path}
    with conn.cursor() as cur:
        cur.execute(
            """
            INSERT INTO memory_chunks (source, doc_id, chunk_id, content, metadata)
            VALUES (%s, %s, %s, %s, %s::jsonb)
            ON CONFLICT (source, doc_id, chunk_id)
            DO UPDATE SET content = EXCLUDED.content, metadata = EXCLUDED.metadata;
            """,
            ("github", rel_path, chunk_id, chunk, json.dumps(metadata)),
        )

def should_include(rel_dir: str, filename: str) -> bool:
    include_files = {"NOVA_PROTOCOL.md", "SESSION_BOOTSTRAP.md", "TASKS_CURRENT.md"}
    if rel_dir == ".":
        return filename.endswith(".md") or filename in include_files
    return rel_dir.startswith("docs") or rel_dir.startswith("brain")

def main():
    db_url = os.environ.get("DATABASE_URL", "")
    if not db_url:
        print("DATABASE_URL missing", flush=True)
        raise SystemExit(1)
    db_url = add_sslmode(db_url)

    try:
        with psycopg.connect(db_url) as conn:
            if not table_exists(conn, "memory_chunks"):
                print("ERROR: table memory_chunks does not exist", flush=True)
                raise SystemExit(2)
    except Exception as e:
        print(f"ERROR: DB connect/query failed: {e}", flush=True)
        raise SystemExit(3)

    root = os.getcwd()
    skip_dirs = {".git", ".github", "node_modules", ".venv", "venv", "__pycache__"}
    files_processed = 0
    total_chunks = 0

    with psycopg.connect(db_url) as conn:
        for dirpath, dirnames, filenames in os.walk(root, topdown=True):
            dirnames[:] = [d for d in dirnames if d not in skip_dirs]
            rel_dir = os.path.relpath(dirpath, root)
            for fname in filenames:
                if not should_include(rel_dir, fname):
                    continue
                rel_path = fname if rel_dir == "." else os.path.join(rel_dir, fname)
                abs_path = os.path.join(dirpath, fname)
                try:
                    with open(abs_path, "r", encoding="utf-8", errors="ignore") as f:
                        text = f.read()
                except Exception:
                    continue
                for i, chunk in enumerate(chunk_text(text)):
                    upsert_chunk(conn, rel_path.replace("\\", "/"), i, chunk)
                    total_chunks += 1
                files_processed += 1

    print(f"ingested_files={files_processed} total_chunks={total_chunks}")

if __name__ == "__main__":
    main()
