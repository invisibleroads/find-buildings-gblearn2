"""
Routines for sending messages
"""
# Import system modules
import smtplib
import email.utils
import email.mime.text
import socket


def sendMessage(fromByValue, toByValue, subject, body):
    'Send a message using SMTP'
    # Prepare
    message = email.mime.text.MIMEText(body)
    message['To'] = email.utils.formataddr((
        toByValue['nickname'],
        toByValue['email'],
    ))
    message['From'] = email.utils.formataddr((
        fromByValue['nickname'], 
        fromByValue['email'],
    ))
    message['Subject'] = subject
    # Connect to server
    if fromByValue['smtp'] == 'localhost':
        server = smtplib.SMTP('localhost')
    else:
        server = smtplib.SMTP_SSL(fromByValue['smtp'], 465)
        if len(fromByValue['username']):
            server.login(fromByValue['username'], fromByValue['password'])
    # Send mail
    try:
        server.sendmail(fromByValue['email'], toByValue['email'], message.as_string())
    except socket.error, error:
        raise Error(error)
    finally:
        server.quit()


class Error(Exception):
    pass
