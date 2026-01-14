"""
Email service module.
Handles sending activation codes via SMTP to the configured mail server.
"""

import smtplib
from email.mime.text import MIMEText
from app.core.config import settings


def send_activation_email(email_to: str, code: str) -> None:
    """
    Sends a 4-digit activation code to the user's email address using SMTP.
    """
    subject: str = "Your Activation Code"
    body: str = f"Your 4-digit activation code is: {code}. It expires in 1 minute."

    msg: MIMEText = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = settings.EMAILS_FROM
    msg["To"] = email_to

    try:
        with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as server:
            server.send_message(msg)
    except (smtplib.SMTPException, ConnectionError) as e:
        # In a real app, you might use a proper logger here
        print(f"Error sending email to {email_to}: {e}")
