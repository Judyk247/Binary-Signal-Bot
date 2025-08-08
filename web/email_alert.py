# web/email_alert.py

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# === Configuration ===
EMAIL_SENDER = "your_email@gmail.com"  # Replace with your Gmail address
EMAIL_PASSWORD = "your_email_password"  # App password or regular password if using less secure apps (not recommended)
EMAIL_RECEIVER = "your_email@gmail.com"  # Where to send alerts (usually admin email)

# === Status Flag ===
EMAIL_ALERTS_ENABLED = False  # Set to True when ready to activate email sending

def send_login_alert(username, ip_address):
    if not EMAIL_ALERTS_ENABLED:
        print(f"[INFO] Email alert disabled. Login by {username} from {ip_address}")
        return

    try:
        subject = "New Login Detected - Trading Bot Dashboard"
        body = f"""
        Hello Admin,

        A new login has been detected on your trading bot dashboard.

        Username: {username}
        IP Address: {ip_address}

        Please review this activity.

        Regards,
        Trading Bot System
        """

        message = MIMEMultipart()
        message["From"] = EMAIL_SENDER
        message["To"] = EMAIL_RECEIVER
        message["Subject"] = subject

        message.attach(MIMEText(body, "plain"))

        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(EMAIL_SENDER, EMAIL_PASSWORD)
            server.send_message(message)

        print(f"[INFO] Login alert email sent for {username}")

    except Exception as e:
        print(f"[ERROR] Failed to send email alert: {e}")
