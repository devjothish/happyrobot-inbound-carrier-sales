import os
from pathlib import Path

from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.config import settings
from app.db import init_db
from app.deps import require_api_key
from app.routers import calls, carriers, loads, metrics

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
    _ensure_seed()


def _ensure_seed() -> None:
    """If loads table is empty (first boot on a fresh volume), seed it."""
    from app.db import SessionLocal
    from app.models import Load

    with SessionLocal() as db:
        if db.query(Load).count() == 0:
            from scripts.seed_loads import seed

            seed()


@app.get("/healthz")
def healthz():
    return {"status": "ok"}


app.include_router(loads.router, dependencies=[Depends(require_api_key)])
app.include_router(carriers.router, dependencies=[Depends(require_api_key)])
app.include_router(calls.router, dependencies=[Depends(require_api_key)])
app.include_router(metrics.router, dependencies=[Depends(require_api_key)])


_static_dir = Path(os.environ.get("STATIC_DIR", "web_static"))
if _static_dir.exists():
    app.mount("/", StaticFiles(directory=str(_static_dir), html=True), name="web")
