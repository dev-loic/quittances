from __future__ import print_function
import os.path
import json
import base64
from requests import HTTPError
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email import encoders
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from datetime import date
import locale
locale.setlocale(locale.LC_TIME,'fr_FR')
import argparse

# Local Imports
from errors import CreatingCopyError, Error
from edit import get_requests
from email_body import TEXT_BODY_FORMAT

## GLOBAL VARIABLES
TODAY = date.today()
PDF_MIME_TYPE = 'application/pdf'
TEMP_OUTPUT_FILE_NAME = 'output.pdf'

# !!! If modifying these scopes, delete the file token.json.
SCOPES = [
    'https://www.googleapis.com/auth/documents',
    'https://www.googleapis.com/auth/drive',
    'https://www.googleapis.com/auth/gmail.send'
]

def main(tenant_email, tenant_name, template_id):
    try:
        creds = retrieve_and_persist_credentials()
        docs_service = build('docs', 'v1', credentials=creds)
        drive_service = build('drive', 'v3', credentials=creds)

        copy_id = copy_template(drive_service, template_id)
        if copy_id is None:
            raise CreatingCopyError

        edit_document(docs_service, copy_id)
        copy_document = retrieve_document(docs_service, copy_id)
        title = copy_document.get('title')
        print('✅ La quittance {0} a été correctement créée'.format(title))

        download_file(drive_service, copy_id)
        print('⬇️ La quittance {0} a été correctement téléchargée 🎉🎉🎉'.format(title))

        send_email(creds, title, tenant_email, tenant_name)
        print("📨 La quittance {0} a été correctement envoyée à {1}".format(title, tenant_email))

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

## DOCS
def retrieve_document(docs_service, id):
    return docs_service.documents().get(documentId=id).execute()

def copy_template(drive_service, doc_id):
    copy_title = get_title()
    body = {
        'name': copy_title
    }
    drive_response = drive_service.files().copy(fileId=doc_id, body=body).execute()
    return drive_response.get('id', None)

## EDIT / CUSTOMIZING
def edit_document(docs_service, id):
    requests = get_requests()
    result = docs_service.documents().batchUpdate(
        documentId=id, body={'requests': requests}).execute()

def get_title():
    return TODAY.strftime("%B_%Y")

## DOWNLOAD
def download_file(drive_service, file_id):
    request = drive_service.files().export_media(
        fileId=file_id, mimeType=PDF_MIME_TYPE)
    with open(TEMP_OUTPUT_FILE_NAME, 'wb') as file:
        downloader = MediaIoBaseDownload(file, request)
        done = False
        while done is False:
            status, done = downloader.next_chunk()
            # print("Download %d%%." % int(status.progress() * 100))

## SEND EMAIL
def send_email(creds, title, tenant_email, tenant_name):
    if tenant_email is not None:
        gmail_service = build('gmail', 'v1', credentials=creds)
        message = MIMEMultipart()
        message['to'] = tenant_email
        message['cc'] = "loic.saillant@gmail.com"
        message['subject'] = "Quittance {}".format(title)

        text = MIMEText(TEXT_BODY_FORMAT.format(tenant_name, TODAY.strftime('%B')))
        message.attach(text)

        main_type, sub_type = PDF_MIME_TYPE.split('/', 1)
        attachment = MIMEBase(main_type, sub_type)
        with open(TEMP_OUTPUT_FILE_NAME, 'rb') as file:
            attachment.set_payload(file.read())
            file.close()
            attachment.add_header('Content-Disposition', 'attachment', filename="{0}.pdf".format(title))
            encoders.encode_base64(attachment)
            message.attach(attachment)

            message_body = {'raw': base64.urlsafe_b64encode(message.as_string().encode()).decode()}

            gmail_service.users().messages().send(userId='me', body=message_body).execute()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Give email and google doc to duplicate id")
    parser.add_argument('--email',
                        help='Email of renter',
                        required=True)
    parser.add_argument('--name',
                        help='Name of renter',
                        required=True)
    parser.add_argument('--id',
                        help='Id of the google doc to duplicate',
                        required=True)
    args = parser.parse_args()
    tenant_email = args.email
    tenant_name = args.name
    template_id = args.id
    main(tenant_email, tenant_name, template_id)
