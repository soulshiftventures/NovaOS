import os, requests

MEMORY_URL = os.environ.get("MEMORY_API_URL")  # Set this on Render for services that need memory

def fetch_context(task_text: str, k: int = 8):
    if not MEMORY_URL:
        return []
    r = requests.get(f"{MEMORY_URL}/search", params={"q": task_text, "k": k}, timeout=30)
    r.raise_for_status()
    return r.json()

def learn(title: str, body: str, tags=None):
    if not MEMORY_URL:
        return {"status":"skipped","reason":"MEMORY_API_URL not set"}
    payload = {
        "source": "historian",
        "doc_id": f"historian/{title.lower().replace(' ','-')}",
        "chunk_id": None,
        "content": body,
        "metadata": {"tags": tags or []}
    }
    r = requests.post(f"{MEMORY_URL}/upsert", json=payload, timeout=60)
    r.raise_for_status()
    return r.json()
