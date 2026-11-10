import logging
import requests

from app.core.config import settings

logger = logging.getLogger(__name__)


def _send(recipient: str, subject: str, html: str) -> None:
    if settings.email_provider == "console":
        logger.info("Development email to %s: %s", recipient, subject)
        return

    if settings.email_provider == "resend":
        if not settings.resend_api_key:
            raise RuntimeError("Resend API key is not configured.")

        import resend

        resend.api_key = settings.resend_api_key
        response = resend.Emails.send({
            "from": settings.email_from,
            "to": [recipient],
            "subject": subject,
            "html": html,
        })
        logger.info("Resend email accepted: %s", response)
        return

    if settings.email_provider == "brevo":
        if not settings.brevo_api_key:
            raise RuntimeError("Brevo API key is not configured.")

        response = requests.post(
            "https://api.brevo.com/v3/smtp/email",
            headers={
                "api-key": settings.brevo_api_key,
                "Content-Type": "application/json",
                "Accept": "application/json",
            },
            json={
                "sender": {
                    "name": "NoteNest",
                    "email": "noteneststoring@gmail.com",
                },
                "to": [{"email": recipient}],
                "subject": subject,
                "htmlContent": html,
            },
            timeout=15,
        )

        if response.status_code not in (200, 201, 202):
            logger.error(
                "Brevo email failed: status=%s response=%s",
                response.status_code,
                response.text,
            )
            response.raise_for_status()

        logger.info("Brevo email accepted: %s", response.json())
        return

    raise RuntimeError("Email provider is not configured correctly.")


def send_verification_email(recipient: str, token: str) -> None:
    url = f"{settings.public_app_url.rstrip('/')}/verify-email?token={token}"
    _send(
        recipient,
        "Verify your NoteNest email",
        f'<p>Verify your NoteNest account: <a href="{url}">Verify email</a></p>',
    )


def send_password_reset_email(recipient: str, token: str) -> None:
    url = f"{settings.public_app_url.rstrip('/')}/reset-password?token={token}"
    _send(
        recipient,
        "Reset your NoteNest password",
        f'<p>Reset your NoteNest password: <a href="{url}">Reset password</a></p>',
    )


def send_notification_email(recipient: str, subject: str, html: str) -> None:
    _send(recipient, subject, html)