from dotenv import load_dotenv
import os
load_dotenv()

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', os.urandom(24))
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        'DATABASE_URL',
        'mssql+pyodbc://testusermicro:testusermicro@sqlserver/authdb?driver=ODBC+Driver+17+for+SQL+Server'
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY', 'super-secret-jwt-key')
    JWT_ACCESS_TOKEN_EXPIRES = int(os.environ.get('JWT_EXP_MINUTES', 60)) * 60
