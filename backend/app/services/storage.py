"""Storage provider abstraction. Google Drive credentials stay server-side."""
from io import BytesIO
from pathlib import Path

from fastapi import HTTPException

from app.core.config import settings


def _require_allowed_backend() -> None:
    if settings.app_env == "production" and settings.storage_backend != "google_drive":
        raise HTTPException(status_code=503, detail="Production storage must be configured as google_drive.")


def _drive_service():
    if not all((settings.google_drive_client_id, settings.google_drive_client_secret, settings.google_drive_refresh_token, settings.google_drive_folder_id)):
        raise HTTPException(status_code=503, detail="Google Drive storage is not configured.")
    from google.auth.transport.requests import Request
    from google.oauth2.credentials import Credentials
    from googleapiclient.discovery import build

    credentials = Credentials(token=None, refresh_token=settings.google_drive_refresh_token, token_uri="https://oauth2.googleapis.com/token", client_id=settings.google_drive_client_id, client_secret=settings.google_drive_client_secret, scopes=["https://www.googleapis.com/auth/drive.file"])
    credentials.refresh(Request())
    return build("drive", "v3", credentials=credentials, cache_discovery=False)


def store(key: str, content: bytes, content_type: str) -> str:
    _require_allowed_backend()
    if settings.storage_backend == "local":
        settings.upload_directory.mkdir(parents=True, exist_ok=True)
        (settings.upload_directory / key).write_bytes(content)
        return key
    if settings.storage_backend != "google_drive":
        raise HTTPException(status_code=500, detail="Unknown storage backend.")
    from googleapiclient.http import MediaIoBaseUpload

    media = MediaIoBaseUpload(BytesIO(content), mimetype=content_type, resumable=False)
    result = _drive_service().files().create(body={"name": key, "parents": [settings.google_drive_folder_id]}, media_body=media, fields="id").execute()
    return result["id"]


def read(key: str) -> bytes:
    _require_allowed_backend()
    if settings.storage_backend == "local":
        path = settings.upload_directory / key
        if not path.is_file():
            raise HTTPException(status_code=404, detail="Note file not found.")
        return path.read_bytes()
    if settings.storage_backend != "google_drive":
        raise HTTPException(status_code=500, detail="Unknown storage backend.")
    from googleapiclient.http import MediaIoBaseDownload

    stream = BytesIO()
    downloader = MediaIoBaseDownload(stream, _drive_service().files().get_media(fileId=key))
    done = False
    while not done:
        _, done = downloader.next_chunk()
    return stream.getvalue()


def delete(key: str) -> None:
    _require_allowed_backend()
    if settings.storage_backend == "local":
        path = settings.upload_directory / key
        if path.is_file():
            path.unlink()
        return
    if settings.storage_backend != "google_drive":
        raise HTTPException(status_code=500, detail="Unknown storage backend.")
    from googleapiclient.errors import HttpError

    try:
        _drive_service().files().delete(fileId=key).execute()
    except HttpError as error:
        if error.resp.status != 404:
            raise
