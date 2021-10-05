from __future__ import print_function
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from datetime import date
from calendar import monthrange
import locale
locale.setlocale(locale.LC_TIME,'fr_FR')

## GLOBAL VARIABLES
TODAY = date.today()

# !!! If modifying these scopes, delete the file token.json.
SCOPES = [
    'https://www.googleapis.com/auth/documents',
    'https://www.googleapis.com/auth/drive'
]

TEMPLATE_ID = '1B2Fw3U51_L7GxDG9DQwKbwTmyPAk8P39bezC52oQEeE'

def main():
    try:
        creds = retrieve_and_persist_credentials()
        docs_service = build('docs', 'v1', credentials=creds)
        drive_service = build('drive', 'v3', credentials=creds)

        copy_id = copy_template(drive_service)
        if copy_id is not None:
            edit_document(docs_service, copy_id)
            copy_document = retrieve_document(docs_service, copy_id)
            print('La quittance {} a été correctement créée 🎉🎉🎉'.format(copy_document.get('title')))

    except:
        print('❌ Error durant la création du document')


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

def copy_template(drive_service):
    copy_title = get_title()
    body = {
        'name': copy_title
    }
    drive_response = drive_service.files().copy(fileId=TEMPLATE_ID, body=body).execute()
    return drive_response.get('id', None)

## EDIT / CUSTOMIZING
def edit_document(docs_service, id):
    (monthly_fee, rental_charge, monthly_total) = get_fees()
    requests = [
        {
            'replaceAllText': {
                'containsText': {
                    'text': '{{period}}',
                    'matchCase':  'true'
                },
                'replaceText': get_period()
            }
        },
        {
            'replaceAllText': {
                'containsText': {
                    'text': '{{monthly-fee}}',
                    'matchCase':  'true'
                },
                'replaceText': monthly_fee
            }
        },
        {
            'replaceAllText': {
                'containsText': {
                    'text': '{{rental-charge}}',
                    'matchCase':  'true'
                },
                'replaceText': rental_charge
            }
        },
        {
            'replaceAllText': {
                'containsText': {
                    'text': '{{monthly-total}}',
                    'matchCase':  'true'
                },
                'replaceText': monthly_total
            }
        },
        {
            'replaceAllText': {
                'containsText': {
                    'text': '{{today-date}}',
                    'matchCase':  'true'
                },
                'replaceText': TODAY.strftime('%d/%m/%y')
            }
        }
    ]
    result = docs_service.documents().batchUpdate(
        documentId=id, body={'requests': requests}).execute()

def get_title():
    return TODAY.strftime("%B_%Y")

def get_period():
    current_month_nb_of_days = monthrange(TODAY.year, TODAY.month)
    first_day = "1er {}".format(TODAY.strftime("%B %Y"))
    last_day = "{} {}".format(current_month_nb_of_days[1], TODAY.strftime("%B %Y"))
    return "{} au {}".format(first_day, last_day)

def get_fees(monthly_total=110.00, rental_charge=7.12):
    monthly_fee = monthly_total - rental_charge
    return (str(monthly_fee), str(rental_charge), str(monthly_total))

if __name__ == '__main__':
    main()
