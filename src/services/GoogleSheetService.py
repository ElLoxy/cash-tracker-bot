import os
import helper
from google.oauth2 import service_account
from googleapiclient.discovery import build
from dotenv import load_dotenv

# load .env
load_dotenv()

class GoogleSheetService:

    def __init__(self, func):
        # create credentials
        credentials = service_account.Credentials.from_service_account_file('src/google-key.json', scopes=['https://www.googleapis.com/auth/spreadsheets'])
        # build service
        self.service = build('sheets', 'v4', credentials=credentials)
        # set range name
        self.range_name = (
            f"{helper.config(f'google_sheet.functions.{func}.sheet_name')}!"
            f"{helper.config(f'google_sheet.functions.{func}.range.total')}"
        )

    def read(self):
        # read sheet
        result = self.service.spreadsheets().values().get(spreadsheetId=os.getenv('SPREADSHEET_ID'), range=self.range_name).execute()
        # return values
        return result.get('values', [])

    def write(self, update_range, body):
        # add new row
        self.service.spreadsheets().values().update(spreadsheetId=os.getenv('SPREADSHEET_ID'), range=update_range, valueInputOption='RAW', body=body).execute()

    def first_empty_row_index(self):
        # retrieve sheet rows
        rows = self.read()
        # return first empty row index
        return len(rows) + 1

    def add_transaction(self, transaction):
        # get first empty row
        first_empty_row = self.first_empty_row_index()
        # set update range
        update_range = f"{helper.config('google_sheet.functions.add_transaction.sheet_name')}!{helper.config('google_sheet.functions.add_transaction.range.from')}{first_empty_row}:{helper.config('google_sheet.functions.add_transaction.range.to')}{first_empty_row}"
        # set values
        values = [transaction['date'], transaction['payment_method'], transaction['category'], transaction['note'], transaction['amount']]
        # set body
        body = { 'values': [values] }
        # write new row
        self.write(update_range, body)

    def get_balance(self):
        rows = self.read()
        return rows