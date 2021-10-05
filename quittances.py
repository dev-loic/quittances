from __future__ import print_function
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials

# If modifying these scopes, delete the file token.json.
SCOPES = [
    'https://www.googleapis.com/auth/documents',
    'https://www.googleapis.com/auth/drive'
]

TEMPLATE_ID = '1B2Fw3U51_L7GxDG9DQwKbwTmyPAk8P39bezC52oQEeE'

def main():
    creds = retrieve_and_persist_credentials()
    docs_service = build('docs', 'v1', credentials=creds)
    drive_service = service = build('drive', 'v3', credentials=creds)

    copy_id = copy_template(drive_service)
    if copy_id is not None:
        copy_document = retrieve_document(docs_service, copy_id)
        print('The title of the document is: {}'.format(copy_document.get('title')))

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

def retrieve_document(docs_service, id):
    return docs_service.documents().get(documentId=id).execute()

def copy_template(drive_service):
    copy_title = 'Ceci est une copie'
    body = {
        'name': copy_title
    }
    drive_response = drive_service.files().copy(fileId=TEMPLATE_ID, body=body).execute()
    return drive_response.get('id', None)

if __name__ == '__main__':
    main()
