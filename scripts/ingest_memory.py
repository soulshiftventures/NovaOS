import os, sys, pathlib, json

# --- DB URL with TLS fallback ---
DB = os.environ.get("DATABASE_URL", "")
if DB and "sslmode=" not in DB:
    DB = f"{DB}{'&' if '?' in DB else '?'}sslmode=require"

# Which files to ingest (no git calls)
INCLUDE_FILES = {
    "NOVA_PROTOCOL.md",
    "SESSION_BOOTSTRAP.md",
    "TASKS_CURRENT.md",
}
INCLUDE_DIR_PREFIXES = ("docs/", "brain/")
INCLUDE_EXTS = (".md",)

def collect_paths(repo_root="."):
    root = pathlib.Path(repo_root)
    skip_dirs = {".git", ".github", ".venv", "venv", "node_modules", "__pycache__"}
    out = []
    for p in root.rglob("*"):
        if p.is_dir():
            # skip heavy/hidden dirs early
            if p.name in skip_dirs:
                # don't descend
                dirs = []
            continue
        rel = p.relative_to(root).as_posix()
        # skip files inside skipped dirs (already handled), else include rules:
        if rel in INCLUDE_FILES:
            out.append(rel)
            continue
        if rel.endswith(INCLUDE_EXTS):
            out.append(rel)
            continue
        if rel.startswith(INCLUDE_DIR_PREFIXES):
            out.append(rel)
            continue
    return out

def chunks(text, size=3000, overlap=300):
    i = 0
    start = 0
    n = len(text)
    while start < n:
        end = min(n, start + size)
        yield i, text[start:end]
        i += 1
        start = end - overlap if end - overlap > start else end

def upsert(conn, doc_id, chunk_id, content):
    with conn.cursor() as cur:
        cur.execute("""
            INSERT INTO memory_chunks (source, doc_id, chunk_id, content, metadata)
            VALUES (%s, %s, %s, %s, %s::jsonb)
            ON CONFLICT (source, doc_id, chunk_id) DO UPDATE
              SET content = EXCLUDED.content,
                  metadata = EXCLUDED.metadata;
        """, ("github", doc_id, f"{doc_id}:{chunk_id}", content, json.dumps({"path": doc_id})))

def main():
    if not DB:
        print("DATABASE_URL missing", file=sys.stderr)
        sys.exit(1)

    # Preflight DB connect + table existence
    try:
        import psycopg
        with psycopg.connect(DB) as c, c.cursor() as cur:
            cur.execute("SELECT to_regclass('public.memory_chunks');")
            if not cur.fetchone()[0]:
                print("ERROR: table memory_chunks does not exist", file=sys.stderr)
                sys.exit(2)
    except Exception as e:
        print(f"ERROR: DB connect/query failed: {e}", file=sys.stderr)
        sys.exit(3)

    paths = collect_paths(".")
    total_chunks = 0
    with psycopg.connect(DB) as conn:
        for rel in paths:
            try:
                text = pathlib.Path(rel).read_text(encoding="utf-8", errors="ignore")
            except Exception:
                continue
            for i, chunk in chunks(text):
                upsert(conn, rel, i, chunk)
                total_chunks += 1
    print(f"ingested_files={len(paths)} total_chunks={total_chunks}")

if __name__ == "__main__":
    main()
