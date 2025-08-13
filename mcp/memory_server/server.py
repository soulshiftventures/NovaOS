import os, json, uuid, time
from fastapi import FastAPI
from pydantic import BaseModel
import redis

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")
NAMESPACE = os.getenv("MCP_NAMESPACE", "nova:mem")

r = redis.from_url(REDIS_URL, decode_responses=True)
app = FastAPI(title="NovaOS MCP Memory Server")

class WriteReq(BaseModel):
    key: str | None = None
    data: dict

class ReadReq(BaseModel):
    key: str

class SearchReq(BaseModel):
    q: str
    limit: int = 20

@app.get("/health")
def health():
    return {"ok": True}

@app.post("/tools/memory.write")
def memory_write(req: WriteReq):
    k = req.key or f"{NAMESPACE}:{uuid.uuid4().hex}"
    r.hset(k, mapping={"payload": json.dumps(req.data), "ts": str(time.time())})
    r.zadd(f"{NAMESPACE}:index", {k: time.time()})
    return {"ok": True, "key": k}

@app.post("/tools/memory.read")
def memory_read(req: ReadReq):
    data = r.hgetall(req.key)
    if not data:
        return {"ok": False, "error": "not_found"}
    return {"ok": True, "data": json.loads(data["payload"]), "ts": float(data["ts"])}

@app.post("/tools/memory.search")
def memory_search(req: SearchReq):
    keys = r.zrevrange(f"{NAMESPACE}:index", 0, req.limit-1)
    out = []
    for k in keys:
        h = r.hgetall(k)
        if not h:
            continue
        payload = json.loads(h.get("payload","{}"))
        if req.q.lower() in json.dumps(payload).lower():
            out.append({"key": k, "data": payload, "ts": float(h.get("ts","0"))})
    return {"ok": True, "results": out}
