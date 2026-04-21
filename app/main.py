from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.db import init_db
from app.deps import require_api_key
from app.routers import carriers, loads

app = FastAPI(title="Carrier Sales API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[o.strip() for o in settings.allowed_origins.split(",")],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def _startup() -> None:
    init_db()


@app.get("/healthz")
def healthz():
    return {"status": "ok"}


app.include_router(loads.router, dependencies=[Depends(require_api_key)])
app.include_router(carriers.router, dependencies=[Depends(require_api_key)])
