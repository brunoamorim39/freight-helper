'''
Handles all email functionality throughout the application
'''
import datetime

from flask import render_template
from flask_jwt_extended import create_access_token
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from python_http_client.exceptions import HTTPError

from __init__ import app, sendgrid_api_key

mail = Mail(app)

def send_creation_confirmation_email(user):
    '''
    Handles sending a confirmation email to the user when they have just attempted to create a new account. User accounts will not be created until they have clicked on the confirmation link
    '''
    token = create_access_token(identity=str(user['email']), fresh=datetime.timedelta(hours=24), expires_delta=datetime.timedelta(hours=24))
    email_message = Mail(
        from_email='support@theparthub.com',
        to_emails=user['email'],
        subject='Confirm registration',
        plain_text_content=render_template(
            'email/register_confirmation.txt',
            user=user['display_name'],
            token=token
        ),
        html_content=render_template(
            'email/register_confirmation.html',
            user=user['display_name'],
            token=token
        )
    )
    try:
        sendgrid_client = SendGridAPIClient(sendgrid_api_key)
        sendgrid_client.send(email_message)
    except HTTPError as error:
        print('Error occurred while delivering a registration confirmation email')
        print(error)

def send_password_reset_email(user):
    '''
    Handles the delivery of the requested password reset email to the user
    '''
    token = create_access_token(identity=str(user['email']), fresh=datetime.timedelta(hours=24), expires_delta=datetime.timedelta(hours=24))
    email_message = Mail(
        from_email='support@theparthub.com',
        to_emails=user['email'],
        subject='Password Reset Requested',
        plain_text_content=render_template(
            'email/reset_password.txt',
            user=user['display_name'],
            token=token
        ),
        html_content=render_template(
            'email/reset_password.html',
            user=user['display_name'],
            token=token
        )
    )
    try:
        sendgrid_client = SendGridAPIClient(sendgrid_api_key)
        sendgrid_client.send(email_message)
    except HTTPError as error:
        print('Error occurred while delivering a password reset email')
        print(error)
