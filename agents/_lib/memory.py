import os, time, uuid, json, requests
from typing import Any, Dict, List, Optional

MCP_MEMORY_URL = os.getenv("MCP_MEMORY_URL")

def _url(path: str) -> str:
    if not MCP_MEMORY_URL:
        raise RuntimeError("MCP_MEMORY_URL not set")
    return MCP_MEMORY_URL.rstrip("/") + path

def mem_write(data: Dict[str, Any], key: Optional[str] = None) -> str:
    """Write/overwrite a record. Returns the key."""
    payload = {"data": data}
    if key:
        payload["key"] = key
    r = requests.post(_url("/tools/memory.write"), json=payload, timeout=10)
    r.raise_for_status()
    return r.json().get("key")

def mem_read(key: str) -> Optional[Dict[str, Any]]:
    r = requests.post(_url("/tools/memory.read"), json={"key": key}, timeout=10)
    if r.ok:
        js = r.json()
        if js.get("ok"):
            return {"key": key, "data": js["data"], "ts": js.get("ts")}
    return None

def mem_search(q: str, limit: int = 50) -> List[Dict[str, Any]]:
    r = requests.post(_url("/tools/memory.search"), json={"q": q, "limit": limit}, timeout=15)
    r.raise_for_status()
    return r.json().get("results", [])

# -------- Task helpers (naive, single-claimer) --------

def enqueue_task(task_type: str, payload: Dict[str, Any], assigned_to: str, created_by: str) -> str:
    task = {
        "type": "task",
        "status": "pending",
        "task_type": task_type,
        "assigned_to": assigned_to,
        "created_by": created_by,
        "payload": payload,
        "ts": time.time(),
        "task_id": uuid.uuid4().hex,
    }
    return mem_write(task, key=f"nova:task:{task['task_id']}")

def find_pending_tasks(for_role: str, limit: int = 20) -> List[Dict[str, Any]]:
    # substring search: look for type task + role + pending
    q = f'"type":"task","status":"pending","assigned_to":"{for_role}"'
    # memory.search is substring-only; this is good enough for now
    return mem_search(q, limit=limit)

def claim_task(task_key: str, claimer: str) -> Optional[Dict[str, Any]]:
    rec = mem_read(task_key)
    if not rec: return None
    data = rec["data"]
    if data.get("status") != "pending":
        return None
    data["status"] = "claimed"
    data["claimed_by"] = claimer
    data["claimed_ts"] = time.time()
    mem_write(data, key=task_key)
    return data

def complete_task(task_key: str, result: Dict[str, Any]) -> None:
    rec = mem_read(task_key)
    if not rec: return
    data = rec["data"]
    data["status"] = "done"
    data["result"] = result
    data["done_ts"] = time.time()
    mem_write(data, key=task_key)

def log_event(agent: str, topic: str, payload: Dict[str, Any]) -> None:
    mem_write({"agent": agent, "type": "event", "topic": topic, "payload": payload, "ts": time.time()})
