from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.auth import router as auth_router
from app.api.v1.health import router as health_router
from app.api.v1.notes import router as notes_router
from app.api.v1.library import router as library_router
from app.api.v1.admin import router as admin_router
from app.core.config import settings

app = FastAPI(title="NoteNest API", version="0.1.0")
app.add_middleware(CORSMiddleware, allow_origins=[settings.frontend_origin], allow_credentials=False, allow_methods=["GET", "POST", "PATCH", "DELETE"], allow_headers=["Authorization", "Content-Type"])
app.include_router(health_router, prefix="/api/v1")
app.include_router(auth_router, prefix="/api/v1")
app.include_router(notes_router, prefix="/api/v1")
app.include_router(library_router, prefix="/api/v1")
app.include_router(admin_router, prefix="/api/v1")
