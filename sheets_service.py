import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime
import os

class SheetsService:
    def __init__(self, credentials_file='credentials.json', spreadsheet_name='SRM Attendance'):
        self.credentials_file = credentials_file
        self.spreadsheet_name = spreadsheet_name
        self.client = None
        self.sheet = None
        self.init_sheets()

    def init_sheets(self):
        try:
            if not os.path.exists(self.credentials_file):
                print("Warning: credentials.json not found")
                return

            scope = [
                'https://spreadsheets.google.com/feeds',
                'https://www.googleapis.com/auth/drive'
            ]

            creds = Credentials.from_service_account_file(
                self.credentials_file, 
                scopes=scope
            )
            self.client = gspread.authorize(creds)

            try:
                spreadsheet = self.client.open(self.spreadsheet_name)
                self.sheet = spreadsheet.sheet1
            except gspread.SpreadsheetNotFound:
                spreadsheet = self.client.create(self.spreadsheet_name)
                self.sheet = spreadsheet.sheet1
                self.sheet.append_row([
                    'Timestamp', 'Roll Number', 'Name', 'Subject', 
                    'Branch', 'Section', 'Status', 'Email'
                ])

        except Exception as e:
            print(f"Google Sheets Error: {e}")

    def record_attendance(self, roll_number, name, subject, branch, section, email):
        try:
            if not self.sheet:
                return False

            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            self.sheet.append_row([
                timestamp, roll_number, name, subject, 
                branch, section, 'Present', email
            ])
            return True
        except Exception as e:
            print(f"Error writing to sheet: {e}")
            return False
