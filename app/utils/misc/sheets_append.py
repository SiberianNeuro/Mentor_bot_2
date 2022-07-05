import httplib2
import os

from apiclient import discovery
from google.oauth2 import service_account

async def add_user_array(state):
    prep = state
    scopes = ["https://www.googleapis.com/auth/drive",
              "https://www.googleapis.com/auth/drive.file",
              "https://www.googleapis.com/auth/spreadsheets"]
    secret_file = os.path.join(os.getcwd(), '../../../client_secret.json')
    credentials = service_account.Credentials.from_service_account_file(secret_file, scopes=scopes)
    service = discovery.build('sheets', 'v4', credentials=credentials)
    spreadsheet_id = "1SNA51rlReIonDCVryC_T3v0wzhU0QrMBfoL_Kxq3Z6w"
    range = "Лист1!A1:J1" if prep['role'] == 8 else "Лист2!A1:J1"
    workday_duration = "8:30-17:00" if prep['traineeship'] in (1, 4) else "10:30-17:00"

    values = [[prep['name'], prep['username'], prep['phone'], prep['city'], "медицинский консультант",
              prep['traineeship'], f"Специальность: {prep['profession']}\nГод поступления: {prep['start_year']}\nГод окончания: {prep['end_year']}",
              workday_duration]]

    body = {
        'majorDimension': "ROWS",
        'values': values
    }

    result = service.spreadsheets().values().append(
        spreadsheetId=spreadsheet_id, range=range, body=body, valueInputOption="USER_ENTERED"
    ).execute()

    print('{0} cells appended.'.format(result.get('updates').get('updatedCells')))
