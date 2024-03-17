import smtplib
from email.mime.text import MIMEText

class Emailer:
    """A class to send emails."""
    def __init__(self, username, password):
        self.server = smtplib.SMTP('smtp.gmail.com', 587)
        self.server.starttls()
        self.server.login(username, password)