# File 6

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from app.config import EMAIL_SENDER, EMAIL_PASSWORD

def send_email(to_email, booking_id, details):
    """Sends a real email using Gmail SMTP."""
    subject = f"Booking Confirmation #{booking_id}"
    body = f"""
    Hello {details['name']},
    
    Your booking for '{details['booking_type']}' is confirmed!
    
    Date: {details['date']}
    Time: {details['time']}
    
    Thank you for choosing us.
    """
    
    try:
        msg = MIMEMultipart()
        msg['From'] = EMAIL_SENDER
        msg['To'] = to_email
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain'))
        
        # Connect to Gmail SMTP
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(EMAIL_SENDER, EMAIL_PASSWORD)
        text = msg.as_string()
        server.sendmail(EMAIL_SENDER, to_email, text)
        server.quit()
        print(f"Email sent successfully to {to_email}")
        return True
    except Exception as e:
        print(f"Failed to send email: {e}")
        return False