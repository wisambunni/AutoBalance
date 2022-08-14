import os
import logging
import pickle
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
import pickle
from google.auth import exceptions
from constants import GOOGLE_SCOPES

from exceptions import SheetIdNotFoundException


class SheetsHelper():
    def __init__(self, sheet_id=None):
        self.__sheet_id = sheet_id
        self.__creds = self.get_creds()
        self.__sheet_service = build('sheets', 'v4', credentials=self.__creds)
        self.__sheet = self.__sheet_service.spreadsheets()

    def get_creds(self):
        creds = None
        # The file token.pickle stores the user's access and refresh tokens, and is
        # created automatically when the authorization flow completes for the first time.
        if os.path.exists('token.pickle'):
            with open('token.pickle', 'rb') as token:
                creds = pickle.load(token)
        # If ther are no (valid) credentails available, let the user log in.
        if not creds or not creds.valid:
            logging.info('Credentials not found, asking user for info')
            if creds and creds.expired and creds.refresh_token:
                try:
                    creds.refresh(Request())
                except exceptions.RefreshError:
                    os.unlink('token.pickle')
                    logging.error(
                        'Credentials could not be refreshed, possibly the authorization has been revoked.')
                    return self.get_creds()
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    'credentials.json', GOOGLE_SCOPES
                )
                creds = flow.run_local_server(port=8080)
            with open('token.pickle', 'wb') as token:
                pickle.dump(creds, token)

        return creds

    def get_values(self, range_name):
        if not self.__sheet_id:
            logging.error('Sheet ID is not found')
            raise SheetIdNotFoundException
        result = self.__sheet.values().get(
            spreadsheetId=self.__sheet_id, range=range_name).execute()
        values = result.get('values', [])

        if not values:
            logging.warning(f'No data was found. for range {range_name}')

        return values

    def update_values(self, range_name, values, value_input_option='USER_ENTERED'):
        if not self.__sheet_id:
            logging.error('Sheet ID is not found')
            raise SheetIdNotFoundException
        body = {
            'values': values
        }
        result = self.__sheet.values().update(spreadsheetId=self.__sheet_id, range=range_name,
                                              valueInputOption=value_input_option, body=body).execute()
        logging.info(f'{result.get("updatedCells")} cells updated.')

        return result

    def set_sheet_id(self, sheet_id):
        self.__sheet_id = sheet_id

    def get_sheet_id(self):
        return self.__sheet_id
