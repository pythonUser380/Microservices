import os
from dotenv import load_dotenv

# Load variables from .env file if present
load_dotenv()

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'invoice-secret')
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        'DATABASE_URL',
        'mssql+pyodbc://testusermicro:testusermicro@db/invoicedb?driver=ODBC+Driver+17+for+SQL+Server'
    )

    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY', 'jwt-invoice-secret')

    # File upload config
    UPLOAD_FOLDER = os.environ.get('UPLOAD_FOLDER', os.path.join(os.getcwd(), 'static', 'uploads'))
    ALLOWED_EXTENSIONS = {'pdf'}

    # Optional logging or debug
    DEBUG = True
