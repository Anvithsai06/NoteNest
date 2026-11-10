"""Run locally to authorize the dedicated NoteNest Drive account.

Requires GOOGLE_DRIVE_CLIENT_ID and GOOGLE_DRIVE_CLIENT_SECRET in the process
environment. This script intentionally prints the refresh token only to the
operator's terminal; store it in the deployment secret manager, never in Git.
"""
import os

from google_auth_oauthlib.flow import InstalledAppFlow

client_id = os.environ.get("GOOGLE_DRIVE_CLIENT_ID")
client_secret = os.environ.get("GOOGLE_DRIVE_CLIENT_SECRET")
if not client_id or not client_secret:
    raise SystemExit("Set GOOGLE_DRIVE_CLIENT_ID and GOOGLE_DRIVE_CLIENT_SECRET first.")

flow = InstalledAppFlow.from_client_config(
    {"installed": {"client_id": client_id, "client_secret": client_secret, "auth_uri": "https://accounts.google.com/o/oauth2/auth", "token_uri": "https://oauth2.googleapis.com/token", "redirect_uris": ["http://localhost"]}},
    scopes=["https://www.googleapis.com/auth/drive.file"],
)
credentials = flow.run_local_server(port=0, access_type="offline", prompt="consent")
if not credentials.refresh_token:
    raise SystemExit("No refresh token returned. Revoke this app's access in Google Account permissions, then retry.")
print("Store this only in your deployment secret manager as GOOGLE_DRIVE_REFRESH_TOKEN:")
print(credentials.refresh_token)
