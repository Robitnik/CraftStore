import smtplib
import ssl
from email.message import EmailMessage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from modules.mail import html_mail

class Email():
    def __init__(self, subject, html_content, recipient_email) -> None:
        self.subject = subject
        self.html_content = html_content
        self.recipient_email = recipient_email


    def send_email(self):
        smtp_server = 'smtp.gmail.com'
        smtp_port = 465
        sender_email = 'aniua.top@gmail.com'
        sender_password = 'thpffoznpoqtnztu'

        message = MIMEMultipart("alternative")
        message['Subject'] = self.subject
        message['From'] = sender_email
        message['To'] = self.recipient_email
        html_content = html_mail.gen_html(title=self.subject, body=self.html_content) 
        html_part = MIMEText(html_content, "html")
        message.attach(html_part)
        try:
            context = ssl.create_default_context()
            with smtplib.SMTP_SSL(smtp_server, smtp_port, context=context) as smtp:
                smtp.login(sender_email, sender_password)
                smtp.send_message(message)

            return True
        except Exception:
            return False
