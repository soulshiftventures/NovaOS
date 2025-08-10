import os, subprocess, sys, pathlib, json

# --- DB URL with TLS fallback ---
DB = os.environ.get("DATABASE_URL", "")
if DB and "sslmode=" not in DB:
    DB = f"{DB}{'&' if '?' in DB else '?'}sslmode=require"

BASE = os.environ.get("BASE_SHA", "")
HEAD = os.environ.get("HEAD_SHA", "")

def run_lines(cmd):
    return subprocess.check_output(cmd, stderr=subprocess.STDOUT).decode().splitlines()

def changed_paths():
    # Try diff between BASE..HEAD, else fall back to all files
    try:
        if BASE and HEAD and BASE != "0000000000000000000000000000000000000000":
            # Ensure SHAs exist in shallow clones
            subprocess.run(["git", "fetch", "--prune", "--unshallow"], check=False)
            return run_lines(["git", "diff", "--name-only", f"{BASE}..{HEAD}"])
    except Exception:
        pass
    try:
        return run_lines(["git", "ls-files"])
    except Exception:
        return []

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

    import psycopg
    # Preflight: connect + table check
    try:
        with psycopg.connect(DB) as c, c.cursor() as cur:
            cur.execute("SELECT to_regclass('public.memory_chunks');")
            if not cur.fetchone()[0]:
                print("ERROR: table memory_chunks does not exist", file=sys.stderr)
                sys.exit(2)
    except Exception as e:
        print(f"ERROR: DB connect/query failed: {e}", file=sys.stderr)
        sys.exit(3)

    paths = changed_paths()
    total_chunks = 0
    with psycopg.connect(DB) as conn:
        for p in paths:
            if not (p.startswith("docs/") or p.startswith("brain/") or p.endswith(".md") or p in ("NOVA_PROTOCOL.md","SESSION_BOOTSTRAP.md","TASKS_CURRENT.md")):
                continue
            try:
                text = pathlib.Path(p).read_text(encoding="utf-8", errors="ignore")
            except Exception:
                continue
            for i, chunk in chunks(text):
                upsert(conn, p, i, chunk)
                total_chunks += 1
    print(f"ingested_files={len([p for p in paths if p])} total_chunks={total_chunks}")

if __name__ == "__main__":
    main()
