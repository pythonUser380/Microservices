from dotenv import load_dotenv
import os

load_dotenv()

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'balance-secret')
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        'DATABASE_URL',
        'mssql+pyodbc://testusermicro:testusermicro@sqlserver/balancedb?driver=ODBC+Driver+17+for+SQL+Server'
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY', 'jwt-secret')
