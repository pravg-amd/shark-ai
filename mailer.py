        import smtplib
        from email.mime.multipart import MIMEMultipart
        from email.mime.text import MIMEText

        # Email credentials from GitHub secrets
        smtp_server = "smtp.gmail.com"
        smtp_port = 465  # Use SSL port for SMTP
        smtp_username = "${{ secrets.GMAIL_USERNAME }}"
        smtp_password = "${{ secrets.GMAIL_PASSWORD }}"

        sender_email = smtp_username
        receiver_email = "praveen.g2@amd.com"  # Replace with recipient's email
        subject = "GitHub Actions Email"
        body = "This is a test email sent from GitHub Actions using Gmail's SMTP server with SSL."

        # Set up the MIME message
        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = receiver_email
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain'))

        try:
            # Connect to Gmail's SMTP server using SSL
            with smtplib.SMTP_SSL(smtp_server, smtp_port) as server:
                server.login(smtp_username, smtp_password)  # Log in to Gmail using your credentials
                server.sendmail(sender_email, receiver_email, msg.as_string())  # Send the email
                print("Email sent successfully")
        except Exception as e:
            print(f"Failed to send email: {e}")
