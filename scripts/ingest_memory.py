import os, subprocess, sys, json, requests, pathlib

MEMORY_API_URL = os.environ["MEMORY_API_URL"]
BASE = os.environ.get("BASE_SHA", "")
HEAD = os.environ.get("HEAD_SHA", "")

def changed_paths():
    if BASE and HEAD and BASE != "0000000000000000000000000000000000000000":
        out = subprocess.check_output(["git", "diff", "--name-only", f"{BASE}..{HEAD}"]).decode().splitlines()
    else:
        out = subprocess.check_output(["git", "ls-files"]).decode().splitlines()
    keep = []
    for p in out:
        if p.startswith("docs/") or p.startswith("brain/") or p.endswith(".md") or p in ("NOVA_PROTOCOL.md","SESSION_BOOTSTRAP.md","TASKS_CURRENT.md"):
            keep.append(p)
    return keep

def chunks(text, size=3000, overlap=300):
    i = 0
    start = 0
    n = len(text)
    while start < n:
        end = min(n, start + size)
        yield i, text[start:end]
        i += 1
        start = end - overlap if end - overlap > start else end

def upsert(doc_id, chunk_id, content):
    payload = {
        "source":"github",
        "doc_id":doc_id,
        "chunk_id":f"{doc_id}:{chunk_id}",
        "content":content,
        "metadata":{"path":doc_id}
    }
    r = requests.post(f"{MEMORY_API_URL}/upsert", json=payload, timeout=60)
    r.raise_for_status()

def main():
    paths = changed_paths()
    total_chunks = 0
    for p in paths:
        try:
            text = pathlib.Path(p).read_text(encoding="utf-8", errors="ignore")
        except Exception:
            continue
        for i, chunk in chunks(text):
            upsert(p, i, chunk)
            total_chunks += 1
    print(f"ingested_files={len(paths)} total_chunks={total_chunks}")

if __name__ == "__main__":
    if not MEMORY_API_URL:
        print("MEMORY_API_URL env missing", file=sys.stderr)
        sys.exit(1)
    main()
