from fastapi import Depends, FastAPI

from app.deps import require_api_key

app = FastAPI(title="Carrier Sales API", version="0.1.0")


@app.get("/healthz")
def healthz():
    return {"status": "ok"}


@app.get("/loads/search", dependencies=[Depends(require_api_key)])
def loads_search_stub():
    return {"loads": []}
