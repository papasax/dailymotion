import smtplib
from email.mime.text import MIMEText
from app.core.config import settings

def send_activation_email(email_to: str, code: str):
    subject = "Your Activation Code"
    body = f"Your 4-digit activation code is: {code}. It expires in 1 minute."
    
    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = settings.EMAILS_FROM
    msg["To"] = email_to

    try:
        with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as server:
            server.send_message(msg)
    except Exception as e:
        print(f"Error sending email: {e}")
