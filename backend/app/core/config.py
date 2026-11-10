from pathlib import Path
from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    database_url: str
    frontend_origin: str = "http://localhost:5173"
    jwt_secret_key: str
    jwt_access_token_minutes: int = 30
    app_env: str = "development"
    public_app_url: str = "http://localhost:5173"
    upload_directory: Path = Path("../storage/uploads")
    email_provider: str = "console"
    brevo_api_key: str | None = None
    email_from: str = "NoteNest <onboarding@resend.dev>"
    storage_backend: str = "local"
    google_drive_client_id: str | None = None
    google_drive_client_secret: str | None = None
    google_drive_refresh_token: str | None = None
    google_drive_folder_id: str | None = None
    malware_scanning_enabled: bool = False
    malware_scanning_required: bool = False
    clamav_host: str = "127.0.0.1"
    clamav_port: int = 3310
    model_config = SettingsConfigDict(env_file=Path(__file__).resolve().parents[2] / ".env", extra="ignore")

    @model_validator(mode="after")
    def require_production_malware_scanning(self):
        if self.app_env == "production" and (not self.malware_scanning_enabled or not self.malware_scanning_required):
            raise ValueError("Production requires enabled and required malware scanning.")
        return self

    @model_validator(mode="after")
    def normalize_postgres_driver(self):
        if self.database_url.startswith("postgresql+psycopg2://"):
            self.database_url = self.database_url.replace("postgresql+psycopg2://", "postgresql+psycopg://", 1)
        elif self.database_url.startswith("postgresql://"):
            self.database_url = self.database_url.replace("postgresql://", "postgresql+psycopg://", 1)
        return self


settings = Settings()
