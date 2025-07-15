from dotenv import load_dotenv
import os
load_dotenv()

class Config:
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        'DATABASE_URL',
        'mssql+pyodbc://testusermicro:testusermicro@sqlserver/splitdb?driver=ODBC+Driver+17+for+SQL+Server'
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.environ.get("SECRET_KEY", "split-secret")
