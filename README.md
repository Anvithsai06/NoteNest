# NoteNest

NoteNest is a verified-college note-sharing MVP. Students register only with an approved college email domain. The first production domain is **`sru.edu.in` (SR University)**; registration uses addresses such as `rollnumber@sru.edu.in`.

## Architecture

| Concern | Development | Production |
| --- | --- | --- |
| Database | Neon PostgreSQL development branch | Neon PostgreSQL |
| Email | Console logger | Resend |
| File storage | `storage/uploads/` | Private Google Drive folder |
| Malware scanning | Disabled by default | Self-hosted ClamAV/clamd, required and fail-closed |

The application uses service abstractions in `backend/app/services/` so email, storage, and malware scanning can be selected entirely through environment variables. No credential is stored in this repository.

## Configuration

Copy `.env.example` to `backend/.env` only if `backend/.env` does not already exist. Do not overwrite an existing environment file or credentials.

Use a Neon pooled or direct PostgreSQL URL with `sslmode=require`:

```env
DATABASE_URL=postgresql+psycopg://<NEON_USER>:<NEON_PASSWORD>@<NEON_HOST>/<NEON_DATABASE>?sslmode=require
APP_ENV=production
FRONTEND_ORIGIN=https://<YOUR_FRONTEND_ORIGIN>
PUBLIC_APP_URL=https://<YOUR_FRONTEND_ORIGIN>
JWT_SECRET_KEY=<GENERATE_A_LONG_RANDOM_SECRET>
```

### Resend

```env
EMAIL_PROVIDER=resend
RESEND_API_KEY=<RESEND_API_KEY>
EMAIL_FROM=NoteNest <verified-sender@your-domain.example>
```

Until a sender domain is verified in Resend, production mail delivery is intentionally not ready. Development uses `EMAIL_PROVIDER=console` and logs verification links instead.

### Google Drive

```env
STORAGE_BACKEND=google_drive
GOOGLE_DRIVE_CLIENT_ID=<OAUTH_CLIENT_ID>
GOOGLE_DRIVE_CLIENT_SECRET=<OAUTH_CLIENT_SECRET>
GOOGLE_DRIVE_REFRESH_TOKEN=<DEDICATED_ACCOUNT_REFRESH_TOKEN>
GOOGLE_DRIVE_FOLDER_ID=<PRIVATE_NOTENEST_FOLDER_ID>
```

The backend uploads files into the configured private folder and saves the returned Google Drive file ID in PostgreSQL. It never creates public links. Every retrieval streams through the authenticated NoteNest backend, so OAuth client secrets and refresh tokens never reach the frontend.

To connect a dedicated NoteNest Gmail/Google Drive account:

1. In Google Cloud Console, create a project and enable the **Google Drive API**.
2. Configure the OAuth consent screen and add the dedicated Gmail account as a test user while the app is unverified.
3. Create an OAuth 2.0 **Desktop app** client for this one-time dedicated-account authorization. Store its client ID and client secret only in your deployment secret manager.
4. On a trusted machine, set those two variables in the shell and run `cd backend && .venv/bin/python scripts/authorize_google_drive.py`. The browser window must sign in only as the dedicated NoteNest account. The helper requests Drive scope `https://www.googleapis.com/auth/drive.file`, offline access, and consent, then prints a refresh token only to that terminal.
5. Create a private `NoteNest` folder in that account's Drive and set `GOOGLE_DRIVE_FOLDER_ID` to its ID. Store the client secret and refresh token only in your deployment secret manager.

Do not share the Drive folder publicly. Google recommends offline access for a server that must refresh access when the user is absent; the backend refreshes the token server-side. [Google OAuth web-server guide](https://developers.google.com/identity/protocols/oauth2/web-server) and [Drive file guide](https://developers.google.com/workspace/drive/api/guides/create-file).

### ClamAV

```env
MALWARE_SCANNING_ENABLED=true
MALWARE_SCANNING_REQUIRED=true
CLAMAV_HOST=<CLAMD_HOST>
CLAMAV_PORT=3310
```

The scanner uses clamd's streaming protocol before any storage write. If required scanning is unavailable or cannot complete, uploads fail closed. Run ClamAV as a separate self-hosted service/container; it is not bundled with the application.

For a single-host deployment, start only the scanner service with:

```bash
docker compose -f docker-compose.clamav.yml up -d
```

The included Compose file binds clamd only to `127.0.0.1:3310`. Do not expose this unencrypted service publicly; for a separate application host, use a private network and set `CLAMAV_HOST` accordingly. [ClamAV Docker documentation](https://docs.clamav.net/manual/Installing/Docker.html)

## Deploying the database

After setting the Neon `DATABASE_URL`, run:

```bash
cd backend
.venv/bin/alembic upgrade head
```

Migration `0004_sru_domain_and_roles` activates `sru.edu.in` and adds explicit roles. It does not create users or credentials.

## Initial SUPER_ADMIN

Register and verify `anvithsai740@gmail.com` first. Then, from the backend directory with the production Neon configuration loaded, run:

```bash
.venv/bin/python scripts/make_admin.py anvithsai740@gmail.com
```

The command refuses to promote a missing or unverified user. It assigns the `super_admin` role.

## Local development

Local development remains usable without production credentials only when explicitly configured:

```env
APP_ENV=development
EMAIL_PROVIDER=console
STORAGE_BACKEND=local
MALWARE_SCANNING_ENABLED=false
```

Point `DATABASE_URL` to a Neon development branch. The frontend runs with `npm run dev` from `frontend/`; the API runs with `.venv/bin/uvicorn app.main:app --reload` from `backend/`.

## Manual setup still required

1. Create a Neon production database/branch and provide its connection URL privately through your deployment environment.
2. Create and verify a Resend sender domain, then supply `RESEND_API_KEY` and `EMAIL_FROM`.
3. Create the dedicated Google account, OAuth client, private NoteNest Drive folder, and backend-only refresh token; then supply the four Google Drive variables.
4. Deploy ClamAV/clamd and set its reachable host/port.
5. Register and verify the initial admin email, run the SUPER_ADMIN command, then rotate any development secrets before deployment.
