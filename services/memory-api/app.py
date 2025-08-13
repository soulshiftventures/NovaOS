from fastapi import FastAPI

app = FastAPI(title="NovaOS Memory API")

@app.get("/")
def root():
    return {"status": "online", "service": "novaos-memory", "version": "0.1.0"}

@app.get("/healthz")
def healthz():
    return {"ok": True}
