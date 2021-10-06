from __future__ import print_function
import os.path
import sys
import json
import base64
from requests import HTTPError
from email.mime.text import MIMEText
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from datetime import date
import locale
locale.setlocale(locale.LC_TIME,'fr_FR')

# Local Imports
from errors import CreatingCopyError, Error
from edit import get_requests

## GLOBAL VARIABLES
TODAY = date.today()

# !!! If modifying these scopes, delete the file token.json.
SCOPES = [
    'https://www.googleapis.com/auth/documents',
    'https://www.googleapis.com/auth/drive',
    'https://www.googleapis.com/auth/gmail.send'
]

## To edit depending on tenant and rental
# TEMPLATE_ID corresponds to the id of _template doc on Google Drive
# TENANT_EMAIL : email of the tenant (None special value if you don't want to send email)
TEMPLATE_ID = "1B2Fw3U51_L7GxDG9DQwKbwTmyPAk8P39bezC52oQEeE"
TENANT_EMAIL = "loic.saillant.dev@gmail.com"

def main():
    try:
        creds = retrieve_and_persist_credentials()
        docs_service = build('docs', 'v1', credentials=creds)
        drive_service = build('drive', 'v3', credentials=creds)

        copy_id = copy_template(drive_service)
        if copy_id is None:
            raise CreatingCopyError

        edit_document(docs_service, copy_id)
        copy_document = retrieve_document(docs_service, copy_id)
        title = copy_document.get('title')
        print('La quittance {} a été correctement créée 🎉🎉🎉'.format(title))

        send_email(creds, title)

    except CreatingCopyError:
        print('❌ La copie n\'a pas pu être créée')
    except HTTPError as error:
        print(error)
    except Error as error:
        print('❌ Error durant la création du document')
        print(error)


## CREDENTIALS
def retrieve_and_persist_credentials():
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json',
                SCOPES
            )
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    return creds

## INFOS
def retrieve_infos(folder_name):
    file_name = "input_infos/{}/infos.json".format(folder_name)
    with open(file_name) as json_file:
        data = json.load(json_file)
        return (data['template_id'], data['tenant_email'])

## DOCS
def retrieve_document(docs_service, id):
    return docs_service.documents().get(documentId=id).execute()

def copy_template(drive_service):
    copy_title = get_title()
    body = {
        'name': copy_title
    }
    drive_response = drive_service.files().copy(fileId=TEMPLATE_ID, body=body).execute()
    return drive_response.get('id', None)

## EDIT / CUSTOMIZING
def edit_document(docs_service, id):
    requests = get_requests()
    result = docs_service.documents().batchUpdate(
        documentId=id, body={'requests': requests}).execute()

def get_title():
    return TODAY.strftime("%B_%Y")

## SEND EMAIL
def send_email(creds, title):
    if TENANT_EMAIL is not None:
        gmail_service = build('gmail', 'v1', credentials=creds)
        message = MIMEText('Ce message est vide 🥸')
        message['to'] = TENANT_EMAIL
        message['subject'] = "Quittance {}".format(title)
        final = {'raw': base64.urlsafe_b64encode(message.as_string().encode()).decode()}

        message = gmail_service.users().messages().send(userId='me', body=final).execute()

if __name__ == '__main__':
    main()
