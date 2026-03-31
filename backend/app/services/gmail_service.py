"""
Gmail OAuth2 Service — sends emails via Gmail API using Google Cloud Console credentials.

Setup (one-time):
1. Go to https://console.cloud.google.com/
2. Create a project (or select an existing one).
3. Enable the **Gmail API** (APIs & Services → Library → search "Gmail API" → Enable).
4. Go to APIs & Services → Credentials → Create Credentials → OAuth client ID.
   - Application type: **Desktop app** (easiest for initial token generation).
   - Download the JSON and save it as  backend/credentials.json
5. Run  `python -m app.services.gmail_service`  once to complete the consent
   flow in your browser.  This creates  backend/token.json  (refresh token).
6. After that the server can send emails headlessly using the stored token.

Environment variables (optional overrides – set in .env):
    GMAIL_CREDENTIALS_FILE  – path to credentials.json  (default: credentials.json)
    GMAIL_TOKEN_FILE        – path to token.json         (default: token.json)
    GMAIL_SENDER_EMAIL      – the "From" address (must match the authorised account)
"""

import os
import base64
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from pathlib import Path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

logger = logging.getLogger(__name__)

# If modifying these scopes, delete token.json and re-authorise.
SCOPES = [
    "https://www.googleapis.com/auth/gmail.send",
    "https://www.googleapis.com/auth/gmail.readonly",
]

# Resolve paths relative to the backend/ directory
_BACKEND_DIR = Path(__file__).resolve().parent.parent.parent  # backend/

CREDENTIALS_FILE = os.getenv(
    "GMAIL_CREDENTIALS_FILE",
    str(_BACKEND_DIR / "credentials.json"),
)
TOKEN_FILE = os.getenv(
    "GMAIL_TOKEN_FILE",
    str(_BACKEND_DIR / "token.json"),
)
SENDER_EMAIL = os.getenv("GMAIL_SENDER_EMAIL", "")


def _get_gmail_credentials() -> Credentials:
    """Return valid Gmail OAuth2 credentials, refreshing or prompting as needed."""
    creds = None

    if os.path.exists(TOKEN_FILE):
        creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)

    # If there are no (valid) credentials, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not os.path.exists(CREDENTIALS_FILE):
                raise FileNotFoundError(
                    f"Google OAuth credentials file not found at {CREDENTIALS_FILE}. "
                    "Download it from Google Cloud Console and place it in backend/credentials.json"
                )
            flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_FILE, SCOPES)
            # Fixed port so the redirect URI is predictable:
            # Register http://localhost:8090/ in Cloud Console if using Web app type
            creds = flow.run_local_server(port=8090, open_browser=True)

        # Save the credentials for the next run
        with open(TOKEN_FILE, "w") as token:
            token.write(creds.to_json())

    return creds


def get_gmail_service():
    """Build and return an authorised Gmail API service instance."""
    creds = _get_gmail_credentials()
    service = build("gmail", "v1", credentials=creds)
    return service


def _build_message(
    to: str,
    subject: str,
    body_html: str,
    sender: str | None = None,
) -> dict:
    """Create a Gmail-compatible message payload."""
    message = MIMEMultipart("alternative")
    message["To"] = to
    message["From"] = sender or SENDER_EMAIL
    message["Subject"] = subject

    # Plain-text fallback
    from html.parser import HTMLParser

    class _StripHTML(HTMLParser):
        def __init__(self):
            super().__init__()
            self._parts: list[str] = []

        def handle_data(self, d):
            self._parts.append(d)

        def get_text(self):
            return "".join(self._parts)

    stripper = _StripHTML()
    stripper.feed(body_html)
    plain_text = stripper.get_text()

    message.attach(MIMEText(plain_text, "plain"))
    message.attach(MIMEText(body_html, "html"))

    raw = base64.urlsafe_b64encode(message.as_bytes()).decode()
    return {"raw": raw}


def send_email(to: str, subject: str, body_html: str, sender: str | None = None) -> dict:
    """
    Send a single email via the Gmail API.

    Parameters
    ----------
    to : str          – recipient email address
    subject : str     – email subject line
    body_html : str   – HTML body of the email
    sender : str      – (optional) override for the From address

    Returns
    -------
    dict – Gmail API response (contains 'id', 'threadId', 'labelIds')
    """
    try:
        service = get_gmail_service()
        message = _build_message(to, subject, body_html, sender)
        result = (
            service.users()
            .messages()
            .send(userId="me", body=message)
            .execute()
        )
        logger.info(f"Email sent to {to}  — Message Id: {result['id']}")
        return result
    except HttpError as error:
        logger.error(f"Gmail API error while sending to {to}: {error}")
        raise


# ── Quick CLI test / first-time token generation ──────────────────────────────
if __name__ == "__main__":
    print("Authorising Gmail credentials …")
    svc = get_gmail_service()
    profile = svc.users().getProfile(userId="me").execute()
    print(f"✅  Authenticated as: {profile['emailAddress']}")
    print(f"   Token saved to:   {TOKEN_FILE}")
