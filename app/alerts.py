from __future__ import annotations

import logging
import smtplib
from email.message import EmailMessage

from app.config import Settings

logger = logging.getLogger(__name__)


def send_email_alert(settings: Settings, subject: str, body: str) -> bool:
    """
    Send an email alert via SMTP if configured.
    Returns True if sent, False if skipped/failed.
    """
    required = (
        settings.smtp_host,
        settings.smtp_user,
        settings.smtp_password,
        settings.smtp_from,
        settings.alert_to,
    )
    if any(v is None for v in required):
        logger.info("Email alerts not configured; skipping send.")
        return False

    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = settings.smtp_from
    msg["To"] = settings.alert_to
    msg.set_content(body)

    try:
        with smtplib.SMTP(settings.smtp_host, settings.smtp_port, timeout=15) as smtp:
            smtp.ehlo()
            if settings.smtp_use_tls:
                smtp.starttls()
                smtp.ehlo()
            smtp.login(settings.smtp_user, settings.smtp_password)
            smtp.send_message(msg)
        logger.info("Email alert sent to %s", settings.alert_to)
        return True
    except Exception:
        logger.exception("Failed to send email alert.")
        return False
