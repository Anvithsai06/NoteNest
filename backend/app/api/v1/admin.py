from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.v1.notes import verified_user
from app.db.dependencies import get_db
from app.models.college_domain import CollegeDomain
from app.models.report import Report
from app.models.user import User
from app.schemas.admin import CollegeDomainRequest, DomainResponse, ReportResponse, ReportStatusRequest

router = APIRouter(prefix="/admin", tags=["admin"])


def admin_user(user: User = Depends(verified_user)) -> User:
    if user.role not in {"admin", "super_admin"}:
        raise HTTPException(status_code=403, detail="Administrator access is required.")
    return user


@router.get("/domains", response_model=list[DomainResponse])
def list_domains(user: User = Depends(admin_user), db: Session = Depends(get_db)) -> list[CollegeDomain]:
    return list(db.scalars(select(CollegeDomain).order_by(CollegeDomain.domain)))


@router.post("/domains", response_model=DomainResponse, status_code=status.HTTP_201_CREATED)
def add_domain(payload: CollegeDomainRequest, user: User = Depends(admin_user), db: Session = Depends(get_db)) -> CollegeDomain:
    domain = payload.domain.strip().lower().removeprefix("@");
    if "." not in domain or " " in domain:
        raise HTTPException(status_code=422, detail="Enter a valid email domain.")
    if db.scalar(select(CollegeDomain).where(CollegeDomain.domain == domain)):
        raise HTTPException(status_code=409, detail="This domain already exists.")
    record = CollegeDomain(domain=domain, college_name=payload.college_name.strip())
    db.add(record); db.commit(); db.refresh(record)
    return record


@router.patch("/domains/{domain_id}", response_model=DomainResponse)
def toggle_domain(domain_id: UUID, is_active: bool, user: User = Depends(admin_user), db: Session = Depends(get_db)) -> CollegeDomain:
    record = db.get(CollegeDomain, domain_id)
    if not record:
        raise HTTPException(status_code=404, detail="Domain not found.")
    record.is_active = is_active
    db.commit(); db.refresh(record)
    return record


@router.get("/reports", response_model=list[ReportResponse])
def list_reports(user: User = Depends(admin_user), db: Session = Depends(get_db)) -> list[Report]:
    return list(db.scalars(select(Report).order_by(Report.created_at.desc())))


@router.patch("/reports/{report_id}")
def update_report(report_id: UUID, payload: ReportStatusRequest, user: User = Depends(admin_user), db: Session = Depends(get_db)) -> dict[str, str]:
    report = db.get(Report, report_id)
    if not report:
        raise HTTPException(status_code=404, detail="Report not found.")
    report.status = payload.status
    db.commit()
    return {"detail": "Report updated."}
