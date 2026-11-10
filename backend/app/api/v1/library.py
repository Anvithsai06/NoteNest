from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.v1.notes import verified_user
from app.db.dependencies import get_db
from app.models.note import Note
from app.models.report import Report
from app.models.saved_note import SavedNote
from app.models.user import User
from app.schemas.library import ReportRequest
from app.schemas.note import NoteResponse

router = APIRouter(tags=["library"])


def public_note_or_404(note_id: UUID, db: Session) -> Note:
    note = db.get(Note, note_id)
    if not note or note.visibility != "public" or note.deletion_status != "active":
        raise HTTPException(status_code=404, detail="Note not found.")
    return note


@router.post("/notes/{note_id}/save", status_code=status.HTTP_204_NO_CONTENT)
def save_note(note_id: UUID, user: User = Depends(verified_user), db: Session = Depends(get_db)) -> None:
    public_note_or_404(note_id, db)
    if not db.get(SavedNote, {"user_id": user.id, "note_id": note_id}):
        db.add(SavedNote(user_id=user.id, note_id=note_id))
        db.commit()


@router.delete("/notes/{note_id}/save", status_code=status.HTTP_204_NO_CONTENT)
def unsave_note(note_id: UUID, user: User = Depends(verified_user), db: Session = Depends(get_db)) -> None:
    saved = db.get(SavedNote, {"user_id": user.id, "note_id": note_id})
    if saved:
        db.delete(saved)
        db.commit()


@router.get("/me/saved-notes", response_model=list[NoteResponse])
def saved_notes(user: User = Depends(verified_user), db: Session = Depends(get_db)) -> list[Note]:
    return list(db.scalars(select(Note).join(SavedNote, SavedNote.note_id == Note.id).where(SavedNote.user_id == user.id, Note.visibility == "public", Note.deletion_status == "active").order_by(SavedNote.created_at.desc())))


@router.get("/me/notes", response_model=list[NoteResponse])
def my_notes(user: User = Depends(verified_user), db: Session = Depends(get_db)) -> list[Note]:
    return list(db.scalars(select(Note).where(Note.uploader_id == user.id).order_by(Note.created_at.desc())))


@router.post("/notes/{note_id}/reports", status_code=status.HTTP_201_CREATED)
def report_note(note_id: UUID, payload: ReportRequest, user: User = Depends(verified_user), db: Session = Depends(get_db)) -> dict[str, str]:
    note = public_note_or_404(note_id, db)
    if note.uploader_id == user.id:
        raise HTTPException(status_code=400, detail="You cannot report your own note.")
    if db.scalar(select(Report).where(Report.note_id == note_id, Report.reporter_id == user.id, Report.status == "open")):
        raise HTTPException(status_code=409, detail="You have already reported this note.")
    db.add(Report(note_id=note_id, reporter_id=user.id, reason=payload.reason, details=payload.details.strip() if payload.details else None))
    db.commit()
    return {"detail": "Report submitted."}
