from fastapi import FastAPI
app = FastAPI(title="NovaOS Dashboard Health")
@app.get("/health")
def health():
    return {"ok": True, "service": "novaos-dashboard"}
