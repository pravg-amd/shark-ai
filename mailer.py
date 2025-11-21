import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import os

# Read credentials from environment variables
smtp_username = os.getenv("GMAIL_USERNAME")
smtp_password = os.getenv("GMAIL_PASSWORD")

smtp_server = "smtp.gmail.com"
smtp_port = 465  # SSL port

sender_email = smtp_username
receiver_email = "praveen.g2@amd.com"   # ← change this
subject = "GitHub Actions Gmail Test"
body = "Hello! This email was sent from GitHub Actions using Gmail SMTP over SSL."

# Create message
msg = MIMEMultipart()
msg["From"] = sender_email
msg["To"] = receiver_email
msg["Subject"] = subject
msg.attach(MIMEText(body, "plain"))

try:
    with smtplib.SMTP_SSL(smtp_server, smtp_port) as server:
        server.login(smtp_username, smtp_password)
        server.sendmail(sender_email, receiver_email, msg.as_string())

    print("Email sent successfully!")

except Exception as e:
    print("Error sending email:", e)
    exit(1)
