NoteNest 📚

A College-Exclusive Academic Notes Sharing Platform

NoteNest is a web-based platform that allows verified college students to upload, organize, discover, search, save, and download academic notes.

The platform restricts registration to approved college email domains to create a trusted academic resource-sharing environment.

The initial supported institution is SR University, with the approved email domain:

@sru.edu.in

Example: [rollno]@sru.edu.in

⸻

1. Features

Student Features

* College email-based registration.
* Email verification and secure authentication.
* JWT-based login and session management.
* Upload academic notes and study materials.
* Browse and discover notes uploaded by other students.
* Search and organize academic resources.
* Download notes securely.
* Save notes to a personal library.
* Report inappropriate or incorrect content.
* Manage personal account information.

Admin Features

* Role-based access control.
* Super Admin privileges.
* Manage approved college email domains.
* Review and manage reported notes.
* Moderate platform content.

Security Features

* Password hashing using Argon2.
* JWT authentication.
* College email domain validation.
* File type and file signature validation.
* Maximum upload size of 25 MB.
* Malware scanning using ClamAV.
* Private Google Drive storage.
* Authenticated file downloads.
* Secure environment-based configuration.
* Reliable file deletion and storage handling.

⸻

2. Technology Stack

Component	Technology
Frontend	React, TypeScript, Vite
Backend	Python, FastAPI
Database	PostgreSQL
Database Hosting	Neon
ORM	SQLAlchemy
Database Migrations	Alembic
Authentication	JWT
Password Hashing	Argon2
Email Service	Brevo Transactional Email API
File Storage	Google Drive API
Malware Detection	ClamAV
Frontend Styling	CSS
Package Management	npm, pip
Version Control	Git and GitHub

⸻

3. System Architecture

                 STUDENT / ADMIN
                        |
                        v
                REACT FRONTEND
                 (Vite + TS)
                        |
                        | HTTP / REST API
                        v
                 FASTAPI BACKEND
                        |
          +-------------+-------------+
          |             |             |
          v             v             v
      NEON DB        BREVO API     GOOGLE DRIVE
    (PostgreSQL)   (Email Service)  (File Storage)
                        |
                        v
                   EMAIL
                 VERIFICATION
                        |
                        v
                     CLAMAV
                (Malware Scanning)

Application Components

Frontend: Provides the user interface for registration, login, note uploads, discovery, saved notes, and administration.

Backend: Handles authentication, authorization, business logic, note management, file validation, and API requests.

Database: Stores users, college domains, notes, saved notes, reports, and email verification records.

Brevo: Sends transactional emails, including account verification emails.

Google Drive: Stores uploaded academic files in a private application folder.

ClamAV: Scans uploaded files for malware before they are stored.

⸻

4. Project Structure

NoteNest/
│
├── backend/
│   ├── alembic/
│   │   └── versions/
│   │
│   ├── app/
│   │   ├── api/
│   │   │   └── v1/
│   │   │       ├── admin.py
│   │   │       ├── auth.py
│   │   │       ├── health.py
│   │   │       ├── library.py
│   │   │       └── notes.py
│   │   │
│   │   ├── core/
│   │   │   └── config.py
│   │   │
│   │   ├── db/
│   │   │   ├── base.py
│   │   │   ├── dependencies.py
│   │   │   └── session.py
│   │   │
│   │   ├── models/
│   │   ├── schemas/
│   │   └── services/
│   │       ├── email_service.py
│   │       ├── file_service.py
│   │       ├── malware_scanner.py
│   │       ├── observability.py
│   │       ├── security.py
│   │       └── storage.py
│   │
│   ├── scripts/
│   ├── tests/
│   ├── requirements.txt
│   ├── alembic.ini
│   └── .env.example
│
├── frontend/
│   ├── src/
│   │   ├── App.tsx
│   │   ├── main.tsx
│   │   └── styles.css
│   ├── package.json
│   ├── package-lock.json
│   └── vite.config.ts
│
├── storage/
│   └── uploads/
│
├── docker-compose.clamav.yml
├── .env.example
├── .gitignore
└── README.md

⸻

5. Prerequisites

Install the following before running NoteNest:

Requirement	Purpose
Python 3.11	Backend development
Node.js and npm	Frontend development
Git	Version control
PostgreSQL / Neon	Database
ClamAV	Malware scanning
Google Cloud account	Google Drive API
Brevo account	Transactional emails

Check your installations:

python3 --version
node --version
npm --version
git --version

⸻

6. Clone the Repository

Clone the project:

git clone https://github.com/Anvithsai06/NoteNest.git

Navigate into the project:

cd NoteNest

⸻

7. Backend Setup

Step 1: Navigate to the backend

cd backend

Step 2: Create a Python virtual environment

python3.11 -m venv .venv

Step 3: Activate the environment

For macOS/Linux:

source .venv/bin/activate

For Windows:

.venv\Scripts\activate

Step 4: Install dependencies

pip install -r requirements.txt

Step 5: Configure environment variables

Create backend/.env using the example configuration as a reference.

From the project root:

cp backend/.env.example backend/.env

Important: Only run this command if backend/.env does not already exist. Never overwrite an existing environment file containing credentials.

Configure the required variables in backend/.env.

Example configuration:

APP_ENV=development
DATABASE_URL=postgresql+psycopg://<USERNAME>:<PASSWORD>@<HOST>/<DATABASE>?sslmode=require
JWT_SECRET_KEY=<YOUR_LONG_RANDOM_SECRET>
FRONTEND_ORIGIN=http://localhost:5173
PUBLIC_APP_URL=http://localhost:5173
EMAIL_PROVIDER=brevo
BREVO_API_KEY=<YOUR_BREVO_API_KEY>
EMAIL_FROM=NoteNest <your-verified-sender@example.com>
STORAGE_BACKEND=google_drive
GOOGLE_DRIVE_CLIENT_ID=<YOUR_CLIENT_ID>
GOOGLE_DRIVE_CLIENT_SECRET=<YOUR_CLIENT_SECRET>
GOOGLE_DRIVE_REFRESH_TOKEN=<YOUR_REFRESH_TOKEN>
GOOGLE_DRIVE_FOLDER_ID=<YOUR_PRIVATE_FOLDER_ID>
MALWARE_SCANNING_ENABLED=true
MALWARE_SCANNING_REQUIRED=true
CLAMAV_HOST=127.0.0.1
CLAMAV_PORT=3310

Replace placeholders with your actual configuration.

Never commit .env files, API keys, database passwords, OAuth credentials, or refresh tokens to GitHub.

⸻

8. Database Setup

NoteNest uses PostgreSQL hosted on Neon.

Step 1: Create a Neon project

1. Create a PostgreSQL project in Neon.
2. Obtain the database connection string.
3. Configure it as DATABASE_URL in backend/.env.
4. Ensure the connection string uses SSL.

Step 2: Apply database migrations

From the backend directory, with the virtual environment activated:

alembic upgrade head

This applies all available database migrations.

To check the current migration version:

alembic current

To view migration history:

alembic history

The migrations create and update the application database schema, including users, notes, saved notes, reports, college domains, and verification tokens.

The initial college domain is:

sru.edu.in

⸻

9. Brevo Email Configuration

NoteNest uses the Brevo Transactional Email API for sending account verification emails.

Setup

1. Create a Brevo account.
2. Verify your sender email address.
3. Generate a transactional email API key.
4. Configure the following in backend/.env:

EMAIL_PROVIDER=brevo
BREVO_API_KEY=<YOUR_BREVO_API_KEY>
EMAIL_FROM=NoteNest <your-verified-sender@example.com>

The backend uses Brevo to send verification emails during registration.

For local development without an email provider, the console email provider can be used if supported by the current configuration:

EMAIL_PROVIDER=console

In console mode, verification information is logged by the backend instead of being delivered through Brevo.

⸻

10. Google Drive Storage Configuration

NoteNest uses Google Drive for private file storage.

Uploaded files are stored in a dedicated Google Drive folder. The application saves the corresponding Drive file ID in PostgreSQL.

Files are retrieved through authenticated backend endpoints rather than publicly shared Drive links.

Setup

1. Create a dedicated Google account for NoteNest storage.
2. Create a Google Cloud project.
3. Enable the Google Drive API.
4. Configure the OAuth consent screen.
5. Create an OAuth 2.0 Desktop application client.
6. Obtain the OAuth client ID and client secret.
7. Create a private Google Drive folder for NoteNest.

Configure:

STORAGE_BACKEND=google_drive
GOOGLE_DRIVE_CLIENT_ID=<CLIENT_ID>
GOOGLE_DRIVE_CLIENT_SECRET=<CLIENT_SECRET>
GOOGLE_DRIVE_REFRESH_TOKEN=<REFRESH_TOKEN>
GOOGLE_DRIVE_FOLDER_ID=<FOLDER_ID>

Generate the Refresh Token

From the backend directory:

.venv/bin/python scripts/authorize_google_drive.py

Follow the browser authorization flow using the dedicated NoteNest Google account.

The script generates a refresh token. Store it securely in your backend environment configuration.

Do not share the Google Drive folder publicly or expose OAuth credentials to the frontend.

⸻

11. ClamAV Malware Scanning

NoteNest integrates ClamAV to scan uploaded files before storage.

The application uses ClamAV’s daemon (clamd) through its TCP interface.

Configuration

MALWARE_SCANNING_ENABLED=true
MALWARE_SCANNING_REQUIRED=true
CLAMAV_HOST=127.0.0.1
CLAMAV_PORT=3310

When malware scanning is required, uploads fail if the scanner is unavailable or cannot complete the scan.

macOS Setup

Install ClamAV using Homebrew:

brew install clamav

Update virus definitions:

freshclam

Start the ClamAV daemon:

/opt/homebrew/opt/clamav/sbin/clamd

Keep this terminal running while using NoteNest.

Alternative: Docker

If using the provided Docker Compose configuration:

docker compose -f docker-compose.clamav.yml up -d

Check the container:

docker compose -f docker-compose.clamav.yml ps

Stop the service:

docker compose -f docker-compose.clamav.yml down

Use only one ClamAV service for the configured host and port. Do not expose the ClamAV TCP service publicly.

⸻

12. Frontend Setup

Open a new terminal and navigate to the frontend directory:

cd frontend

Install dependencies:

npm install

Start the Vite development server:

npm run dev

The frontend will be available at:

http://localhost:5173

⸻

13. Running the Complete Application

For local development on macOS, use three terminal windows.

Terminal 1 — ClamAV

cd ~/Documents/ChatGPT/NoteNest
/opt/homebrew/opt/clamav/sbin/clamd

If ClamAV is already running, do not start another instance.

Terminal 2 — Backend

cd ~/Documents/ChatGPT/NoteNest/backend
source .venv/bin/activate
uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload

Backend:

http://127.0.0.1:8000

Terminal 3 — Frontend

cd ~/Documents/ChatGPT/NoteNest/frontend
npm run dev

Frontend:

http://localhost:5173

Application URLs

Service	URL
Frontend	http://localhost:5173
Backend	http://127.0.0.1:8000
API Documentation	http://127.0.0.1:8000/docs
Alternative API Documentation	http://127.0.0.1:8000/redoc

Keep all required services running while testing the application.

⸻

14. Initial Super Admin Setup

NoteNest supports role-based access control.

To create the initial Super Admin:

1. Register using an approved college email address.
2. Verify the account.
3. Navigate to the backend directory.
4. Run the following command:

.venv/bin/python scripts/make_admin.py <VERIFIED_EMAIL>

Example:

.venv/bin/python scripts/make_admin.py student@sru.edu.in

The script checks that the user exists and has verified their email before assigning the super_admin role.

Do not expose administrative credentials or promote unverified accounts.

⸻

15. Testing

Run backend tests from the backend directory:

cd backend
source .venv/bin/activate
pytest

Run the frontend production build:

cd frontend
npm run build

These commands help verify backend functionality and frontend compilation.

⸻

16. Useful Development Commands

Backend

Start the backend:

uvicorn app.main:app --reload

Run tests:

pytest

Apply migrations:

alembic upgrade head

Check migrations:

alembic current

Frontend

Install dependencies:

npm install

Start development server:

npm run dev

Build for production:

npm run build

Preview production build:

npm run preview

⸻

17. Git and GitHub Workflow

Repository:

https://github.com/Anvithsai06/NoteNest

Check project status:

git status

Stage changes:

git add .

Commit changes:

git commit -m "Describe your changes"

Push changes:

git push

Pull the latest changes:

git pull

⸻

18. Security Considerations

* Never commit .env files or credentials.
* Keep database credentials and API keys server-side.
* Use a strong, randomly generated JWT secret.
* Use verified college email domains for registration.
* Keep Google Drive files private.
* Route file downloads through authenticated backend endpoints.
* Validate uploaded file extensions and signatures.
* Enforce upload size limits.
* Keep ClamAV enabled and required in production.
* Use HTTPS in production.
* Restrict administrative privileges.
* Rotate credentials if they are accidentally exposed.

⸻

19. Deployment Checklist

Before deploying NoteNest:

* Configure the production Neon PostgreSQL database.
* Set production environment variables.
* Generate a secure JWT secret.
* Configure and verify the Brevo sender.
* Configure Google Drive OAuth credentials.
* Create the private NoteNest Drive storage folder.
* Deploy and configure ClamAV.
* Apply database migrations.
* Configure frontend and backend production URLs.
* Configure HTTPS.
* Register and verify the initial administrator.
* Promote the administrator to Super Admin.
* Test registration and email verification.
* Test note uploads, downloads, and deletion.
* Test malware scanning and failure handling.

⸻

20. Current Project Status

Module	Implementation
Student Registration	Implemented
Email Verification	Implemented
Authentication	Implemented
Role-Based Access	Implemented
Notes Upload	Implemented
Notes Discovery	Implemented
Notes Download	Implemented
Saved Notes	Implemented
Reports	Implemented
Admin Management	Implemented
Neon PostgreSQL Integration	Implemented
Brevo Email Integration	Implemented
Google Drive Integration	Implemented
ClamAV Integration	Implemented
Upload Security Validation	Implemented
File Deletion Reliability	Implemented

⸻

21. Future Enhancements

Potential future improvements include:

* Advanced note search and filtering.
* Subject-wise and semester-wise organization.
* Note ratings and reviews.
* User profiles and contribution statistics.
* Improved content moderation.
* Notifications for newly uploaded notes.
* Analytics dashboard for administrators.
* Mobile-friendly experience and mobile application.

⸻

22. Author

Anvith Sai

B.Tech – Computer Science and Engineering (AI & ML)
SR University

GitHub: https://github.com/Anvithsai06

⸻

NoteNest — Share Knowledge. Learn Together.