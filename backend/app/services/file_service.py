from pathlib import Path
from uuid import uuid4
from zipfile import BadZipFile, ZipFile
from fastapi import HTTPException, UploadFile
from app.services.malware_scanner import scan_bytes
from app.services.storage import store

ALLOWED_EXTENSIONS = {".pdf", ".doc", ".docx", ".ppt", ".pptx", ".xls", ".xlsx", ".txt", ".jpg", ".jpeg", ".png"}
MAX_FILE_SIZE = 25 * 1024 * 1024
OLE_SIGNATURE = b"\xd0\xcf\x11\xe0\xa1\xb1\x1a\xe1"


def detect_mime_type(content: bytes, extension: str) -> str:
    if extension == ".pdf" and content.startswith(b"%PDF-"):
        return "application/pdf"
    if extension == ".png" and content.startswith(b"\x89PNG\r\n\x1a\n"):
        return "image/png"
    if extension in {".jpg", ".jpeg"} and content.startswith(b"\xff\xd8\xff"):
        return "image/jpeg"
    if extension in {".doc", ".xls", ".ppt"} and content.startswith(OLE_SIGNATURE):
        return {".doc": "application/msword", ".xls": "application/vnd.ms-excel", ".ppt": "application/vnd.ms-powerpoint"}[extension]
    if extension in {".docx", ".xlsx", ".pptx"}:
        from io import BytesIO
        try:
            with ZipFile(BytesIO(content)) as archive:
                names = set(archive.namelist())
        except BadZipFile:
            names = set()
        expected = {".docx": "word/", ".xlsx": "xl/", ".pptx": "ppt/"}[extension]
        if "[Content_Types].xml" in names and any(name.startswith(expected) for name in names):
            return {".docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document", ".xlsx": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", ".pptx": "application/vnd.openxmlformats-officedocument.presentationml.presentation"}[extension]
    if extension == ".txt":
        try:
            content.decode("utf-8")
            return "text/plain"
        except UnicodeDecodeError:
            pass
    raise HTTPException(status_code=415, detail="File content does not match its extension.")


async def save_upload(upload: UploadFile, directory: Path) -> tuple[str, str, int, str]:
    original_name = Path(upload.filename or "").name
    extension = Path(original_name).suffix.lower()
    if not original_name or extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=415, detail="This file type is not supported.")
    content = await upload.read(MAX_FILE_SIZE + 1)
    if not content or len(content) > MAX_FILE_SIZE:
        raise HTTPException(status_code=413, detail="Files must be between 1 byte and 25 MB.")
    detected_mime_type = detect_mime_type(content, extension)
    stored_name = f"{uuid4().hex}{extension}"
    scan_bytes(content)
    storage_id = store(stored_name, content, detected_mime_type)
    return original_name, storage_id, len(content), detected_mime_type
