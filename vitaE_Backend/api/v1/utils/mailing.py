#!/usr/bin/python3
"""Module for sending emails via Gmail API"""
import os
import base64
from email.mime.text import MIMEText
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.errors import HttpError
from googleapiclient.discovery import build

SCOPES = ['https://www.googleapis.com/auth/gmail.send']
"""Scopes required for sending emails"""


def get_gmail_credentials():
    """Getting and return Gmail API credentials"""
    api_credn = None
    if os.path.exists('token.json'):
        api_credn = Credentials.from_authorized_user_file('token.json', SCOPES)
    if not api_credn or not api_credn.valid:
        if api_credn and api_credn.expired and api_credn.refresh_token:
            api_credn.refresh(Request())
        else:
            oauth_flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            api_credn = oauth_flow.run_local_server(
                host=os.getenv('HOST', '0.0.0.0'),
                port=5050,
                open_browser=False
            )
        with open('token.json', 'w') as token:
            token.write(api_credn.to_json())
    return api_credn


def create_email_message(recipient, subject, body_html):
    """Create MIME message for email"""
    message = MIMEText(body_html, 'html', 'utf-8')
    message['to'] = recipient
    message['from'] = os.getenv('GMAIL_SENDER')
    message['subject'] = subject
    encoded_message = {'raw': base64.urlsafe_b64encode(
        bytes(message.as_string(), 'utf-8')).decode('utf-8')
    }
    return encoded_message


def send_email(service, message):
    """Sending messages witn email using Gmail API"""
    try:
        gmail_credn = get_gmail_credentials()
        service = build('gmail', 'v1', credentials=gmail_credn)
        message = (service.users().messages().send(userId='me', body=message)
                   .execute())
        print(f"Message Id: {message['id']}")
        return message
    except HttpError as error:
        print(f'An error occured: {error}')


def deliver_message(dest, subject, body_html):
    """Deliver to destination user the message"""
    try:
        api_credn = get_gmail_credentials()
        service = build('gmail', 'v1', credentials=api_credn)
        message = create_email_message(dest, subject, body_html)
        send_email(service, message)
    except HttpError as error:
        print(f'An error occurred: {error}')
