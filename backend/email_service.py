"""
Email service for sending thank-you emails after feedback submission.
Uses Gmail SMTP with App Password. Set credentials in backend/.env
"""

import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))

SMTP_HOST = os.getenv("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USER = os.getenv("SMTP_USER", "")
SMTP_PASS = os.getenv("SMTP_PASS", "")


def send_thank_you_email(to_email: str, name: str, category: str) -> None:
    if not SMTP_USER or not SMTP_PASS:
        print("[email_service] SMTP credentials not set — skipping email.")
        return

    subject = "Thank you for your feedback!"

    html = f"""
    <html>
    <body style="font-family: Arial, sans-serif; background: #f4f4f4; padding: 30px;">
      <div style="max-width: 500px; margin: auto; background: white; border-radius: 10px; padding: 30px; box-shadow: 0 2px 8px rgba(0,0,0,0.1);">
        <h2 style="color: #2196F3;">Thank You, {name}! 🙏</h2>
        <p style="font-size: 16px; color: #333;">
          We received your feedback and truly appreciate you taking the time to share your thoughts with us.
        </p>
        <div style="background: #f0f7ff; border-left: 4px solid #2196F3; padding: 12px 16px; border-radius: 4px; margin: 20px 0;">
          <strong>Feedback Type:</strong> {category}
        </div>
        <p style="font-size: 15px; color: #555;">
          Your input helps us improve and deliver a better experience for everyone.
          We will review your feedback and take the necessary action.
        </p>
        <p style="font-size: 15px; color: #555;">
          Thanks again for being part of our community!
        </p>
        <br>
        <p style="color: #888; font-size: 13px;">— The Feedback Team</p>
      </div>
    </body>
    </html>
    """

    msg = MIMEMultipart("alternative")
    msg["From"] = SMTP_USER
    msg["To"] = to_email
    msg["Subject"] = subject
    msg.attach(MIMEText(html, "html"))

    try:
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USER, SMTP_PASS)
            server.sendmail(SMTP_USER, to_email, msg.as_string())
        print(f"[email_service] Thank-you email sent to {to_email}")
    except Exception as e:
        print(f"[email_service] Failed to send email: {e}")
        raise
