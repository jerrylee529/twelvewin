# project/email.py

from flask_mail import Message

from app import app, mail

from sendmail import send_mail

def send_email(to, subject, template):
    '''
    msg = Message(
        subject,
        recipients=[to],
        html=template,
        sender=app.config['MAIL_DEFAULT_SENDER']
    )
    mail.send(msg)
    '''
    send_mail(subject=subject, mailto=to, content=template, attachments=None)
