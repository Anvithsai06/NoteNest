from fastapi import APIRouter
from fastapi import HTTPException

from app.services.malware_scanner import scanner_ready

router = APIRouter(tags=["health"])


@router.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@router.get("/health/clamav")
def clamav_health() -> dict[str, str]:
    if not scanner_ready():
        raise HTTPException(status_code=503, detail="ClamAV is unavailable.")
    return {"status": "ok"}
