"""
Email service module.
Handles sending activation codes via SMTP to the configured mail server.
"""

import logging
from email.mime.text import MIMEText
import aiosmtplib
from app.core.config import settings

logger = logging.getLogger(__name__)


async def send_activation_email(email_to: str, code: str) -> None:
    """
    Sends a 4-digit activation code using aiosmtplib (asynchronous).
    """
    subject: str = "Your Activation Code"
    body: str = f"Your 4-digit activation code is: {code}. It expires in 1 minute."

    msg: MIMEText = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = settings.EMAILS_FROM
    msg["To"] = email_to

    try:
        # Utilisation de aiosmtplib.send pour un envoi rapide
        await aiosmtplib.send(
            msg,
            hostname=settings.SMTP_HOST,
            port=settings.SMTP_PORT,
        )
        logger.info("Activation email sent asynchronously to %s", email_to)
    except (aiosmtplib.SMTPException, ConnectionError) as e:
        logger.error("Error sending async email to %s: %s", email_to, e)
