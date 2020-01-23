from django.conf import settings
import requests
import smtplib
from email.mime.text import MIMEText

class Mailer():

    def send_email(self, recipient, message):
        try:
            # START confirmation email

            sender = 'no-reply@telegents.com'
            message = message
            msg = MIMEText(message, 'html')
            msg['Subject'] = "Telegents: Registration"
            msg['From'] = sender
            msg['To'] = recipient

            server = smtplib.SMTP_SSL(settings.EMAIL_HOST, settings.EMAIL_PORT)
            server.login(settings.EMAIL_HOST_USER, settings.EMAIL_HOST_PASSWORD)
            server.sendmail(sender, [recipient], msg.as_string())
            server.quit()

            # END confirmation email
            return True
        except:
            return False