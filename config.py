import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    UPLOAD_FOLDER = os.environ.get('UPLOAD_FOLDER') or 'static/uploads/faces'
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024

    DATABASE_URL = os.environ.get('DATABASE_URL') or 'sqlite:///attendance.db'

    EMAIL_USER = os.environ.get('EMAIL_USER')
    EMAIL_PASS = os.environ.get('EMAIL_PASS')
    SMTP_SERVER = os.environ.get('SMTP_SERVER', 'smtp.gmail.com')
    SMTP_PORT = int(os.environ.get('SMTP_PORT', 587))

    SPREADSHEET_NAME = os.environ.get('SPREADSHEET_NAME', 'SRM Attendance')

    FACE_TOLERANCE = float(os.environ.get('FACE_TOLERANCE', 0.6))
