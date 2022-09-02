from pathlib import Path
from loguru import logger
import typing
import inspect

from apiclient import discovery
from google.oauth2 import service_account
from googleapiclient.errors import HttpError


class GoogleSheetsApi:
    """
    Usable class for operations on google sheets
    """
    __scopes = ["https://www.googleapis.com/auth/drive",
                "https://www.googleapis.com/auth/drive.file",
                "https://www.googleapis.com/auth/spreadsheets"]
    __secret_file = Path(Path(__file__).parent, 'client_secret.json')
    __credentials = service_account.Credentials.from_service_account_file(str(__secret_file), scopes=__scopes)
    __service = discovery.build('sheets', 'v4', credentials=__credentials)

    def __init__(self, spreadsheet_id: str = None, spreadsheet_range: str = None):
        """
        Creating an object for a specific page and range
        :param spreadsheet_id: unique ID for each spreadsheet from google-sheets
        :param spreadsheet_range: <sheet_name>!<start_cell>:<end_cell>. Example: Sheet1!A1:B1
        """
        self.__spreadsheet_id = spreadsheet_id
        self.__spreadsheet_range = spreadsheet_range

    def __enter__(self):
        return self

    def __exit__(self, *ext_info):
        del self

    @property
    def spreadsheet_id(self):
        return self.__spreadsheet_id

    @property
    def spreadsheet_range(self):
        return self.__spreadsheet_range

    @spreadsheet_id.setter
    def spreadsheet_id(self, value):
        self.__spreadsheet_id = value

    @spreadsheet_range.setter
    def spreadsheet_range(self, value):
        self.__spreadsheet_range = value

    def append_values(
            self,
            values: typing.Iterable[typing.Iterable[typing.Any]],
            value_input_option: str = "USER_ENTERED",
            major_dimension: str = "ROWS"
    ):

        body = {
            'majorDimension': major_dimension,
            'values': values
        }

        try:
            result = GoogleSheetsApi.__service.spreadsheets().values().append(
                spreadsheetId=self.__spreadsheet_id,
                range=self.__spreadsheet_range,
                body=body,
                valueInputOption=value_input_option
            ).execute()
            logger.info('{0} rows appended'.format(result.get('updates').get('updatedRows')))
        except HttpError as e:
            logger.error(e)

    def clear_values(self):
        body = {}
        try:
            result = GoogleSheetsApi.__service.spreadsheets().values().clear(
                spreadsheetId=self.__spreadsheet_id, range=self.__spreadsheet_range, body=body
            ).execute()
            logger.info(f'Deleted all values from {result["clearedRange"]}')
        except HttpError as e:
            logger.error(e)

    def get_values(
            self,
            value_render_option: str = "FORMATTED_VALUE",
            date_time_render_option: str = "SERIAL_NUMBER",
            major_dimension: str = "ROWS"
    ):
        try:
            result = GoogleSheetsApi.__service.spreadsheets().values().get(
                spreadsheetId=self.__spreadsheet_id, range=self.__spreadsheet_range,
                valueRenderOption=value_render_option,
                dateTimeRenderOption=date_time_render_option,
                majorDimension=major_dimension
            ).execute()
            return result
        except HttpError as e:
            logger.error(e)



