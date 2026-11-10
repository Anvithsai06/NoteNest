import logging
from datetime import UTC, datetime
from uuid import UUID
import jwt
from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from fastapi.responses import Response
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session
from app.core.config import settings
from app.db.dependencies import get_db
from app.models.note import Note
from app.models.user import User
from app.schemas.note import NoteResponse, NoteUpdate
from app.services.file_service import save_upload
from app.services.storage import delete as delete_stored_file
from app.services.storage import read as read_stored_file
from app.services.observability import log_event

router = APIRouter(prefix="/notes", tags=["notes"])
bearer = HTTPBearer()
logger = logging.getLogger(__name__)


def verified_user(credentials: HTTPAuthorizationCredentials = Depends(bearer), db: Session = Depends(get_db)) -> User:
    try:
        user_id = UUID(jwt.decode(credentials.credentials, settings.jwt_secret_key, algorithms=["HS256"])["sub"])
    except (jwt.InvalidTokenError, KeyError, ValueError):
        raise HTTPException(status_code=401, detail="Invalid authentication token.")
    user = db.get(User, user_id)
    if not user or not user.is_active or not user.is_email_verified:
        raise HTTPException(status_code=401, detail="Invalid authentication token.")
    return user


@router.post("", response_model=NoteResponse, status_code=201)
async def upload_note(title: str = Form(..., min_length=2, max_length=200), subject: str = Form(..., min_length=2, max_length=120), description: str | None = Form(None, max_length=5000), course_code: str | None = Form(None, max_length=80), semester: str | None = Form(None, max_length=50), file: UploadFile = File(...), user: User = Depends(verified_user), db: Session = Depends(get_db)) -> Note:
    original, stored, size, mime = await save_upload(file, settings.upload_directory)
    note = Note(uploader_id=user.id, title=title.strip(), description=description.strip() if description else None, subject=subject.strip(), course_code=course_code.strip() if course_code else None, semester=semester.strip() if semester else None, college_name=user.college_name, original_filename=original, stored_filename=stored, storage_path=stored, mime_type=mime, file_size_bytes=size)
    try:
        db.add(note)
        db.commit()
        db.refresh(note)
    except SQLAlchemyError as error:
        db.rollback()
        try:
            delete_stored_file(stored)
        except Exception as cleanup_error:
            log_event(logger, logging.ERROR, "upload_compensation_failed", storage_file_id=stored, error_type=type(cleanup_error).__name__)
        log_event(logger, logging.ERROR, "upload_database_persistence_failed", storage_file_id=stored, error_type=type(error).__name__)
        raise HTTPException(status_code=503, detail="Upload could not be completed; please try again.") from error
    log_event(logger, logging.INFO, "upload_completed", note_id=str(note.id), uploader_id=str(user.id))
    return note


@router.get("", response_model=list[NoteResponse])
def list_notes(q: str | None = None, subject: str | None = None, course_code: str | None = None, semester: str | None = None, page: int = 1, page_size: int = 20, user: User = Depends(verified_user), db: Session = Depends(get_db)) -> list[Note]:
    if page < 1 or not 1 <= page_size <= 50:
        raise HTTPException(status_code=422, detail="Page must be positive and page size must be between 1 and 50.")
    query = select(Note).where(Note.visibility == "public", Note.deletion_status == "active")
    if q:
        query = query.where(Note.title.ilike(f"%{q.strip()}%"))
    if subject:
        query = query.where(Note.subject == subject.strip())
    if course_code:
        query = query.where(Note.course_code == course_code.strip())
    if semester:
        query = query.where(Note.semester == semester.strip())
    return list(db.scalars(query.order_by(Note.created_at.desc()).offset((page - 1) * page_size).limit(page_size)))


@router.get("/{note_id}", response_model=NoteResponse)
def get_note(note_id: UUID, user: User = Depends(verified_user), db: Session = Depends(get_db)) -> Note:
    note = db.get(Note, note_id)
    if not note or note.visibility != "public" or note.deletion_status != "active":
        raise HTTPException(status_code=404, detail="Note not found.")
    return note


@router.get("/{note_id}/download")
def download_note(note_id: UUID, user: User = Depends(verified_user), db: Session = Depends(get_db)) -> Response:
    note = db.get(Note, note_id)
    if not note or note.visibility != "public" or note.deletion_status != "active":
        raise HTTPException(status_code=404, detail="Note not found.")
    note.download_count += 1
    db.commit()
    content = read_stored_file(note.storage_path)
    return Response(content=content, media_type=note.mime_type, headers={"Content-Disposition": f'attachment; filename="{note.original_filename}"'})


@router.patch("/{note_id}", response_model=NoteResponse)
def update_note(note_id: UUID, payload: NoteUpdate, user: User = Depends(verified_user), db: Session = Depends(get_db)) -> Note:
    note = db.get(Note, note_id)
    if not note or note.uploader_id != user.id:
        raise HTTPException(status_code=404, detail="Note not found.")
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(note, field, value.strip() if isinstance(value, str) else value)
    db.commit()
    db.refresh(note)
    return note


@router.delete("/{note_id}", status_code=204)
def delete_note(note_id: UUID, user: User = Depends(verified_user), db: Session = Depends(get_db)) -> None:
    note = db.get(Note, note_id)
    if not note or note.uploader_id != user.id:
        raise HTTPException(status_code=404, detail="Note not found.")
    if note.deletion_status == "active":
        note.deletion_status = "pending_deletion"
        note.visibility = "hidden"
        note.deletion_requested_at = datetime.now(UTC)
        try:
            db.commit()
        except SQLAlchemyError as error:
            db.rollback()
            log_event(logger, logging.ERROR, "delete_mark_failed", note_id=str(note_id), error_type=type(error).__name__)
            raise HTTPException(status_code=503, detail="Deletion could not be started; please try again.") from error
    if _finalize_deletion(note, db):
        return
    raise HTTPException(status_code=202, detail="Deletion is pending and will be retried.")


@router.post("/{note_id}/retry-deletion", status_code=204)
def retry_deletion(note_id: UUID, user: User = Depends(verified_user), db: Session = Depends(get_db)) -> None:
    note = db.get(Note, note_id)
    if not note or note.uploader_id != user.id:
        raise HTTPException(status_code=404, detail="Note not found.")
    if note.deletion_status != "pending_deletion":
        raise HTTPException(status_code=409, detail="Note is not pending deletion.")
    if _finalize_deletion(note, db):
        return
    raise HTTPException(status_code=202, detail="Deletion remains pending; retry later.")


def _finalize_deletion(note: Note, db: Session) -> bool:
    note.deletion_attempts += 1
    try:
        delete_stored_file(note.storage_path)
    except Exception as error:
        note.last_deletion_error = type(error).__name__[:200]
        try:
            db.commit()
        except SQLAlchemyError:
            db.rollback()
        log_event(logger, logging.ERROR, "storage_delete_failed", note_id=str(note.id), storage_file_id=note.storage_path, attempt=note.deletion_attempts, error_type=type(error).__name__)
        return False
    try:
        db.delete(note)
        db.commit()
    except SQLAlchemyError as error:
        db.rollback()
        log_event(logger, logging.ERROR, "deletion_database_finalize_failed", note_id=str(note.id), error_type=type(error).__name__)
        return False
    log_event(logger, logging.INFO, "deletion_completed", note_id=str(note.id))
    return True
