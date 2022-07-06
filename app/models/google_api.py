import httplib2
import os

from apiclient import discovery
from google.oauth2 import service_account


def google_api():
    scopes = ["https://www.googleapis.com/auth/drive",
                  "https://www.googleapis.com/auth/drive.file",
                  "https://www.googleapis.com/auth/spreadsheets"]
    secret_file = os.path.join(os.getcwd(), '../../client_secret.json')
    credentials = service_account.Credentials.from_service_account_file(secret_file, scopes=scopes)
    service = discovery.build('sheets', 'v4', credentials=credentials)

    return service
