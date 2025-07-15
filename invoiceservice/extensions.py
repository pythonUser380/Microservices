# invoiceservice/extensions.py
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from sqlalchemy.orm import Session

db = SQLAlchemy()
jwt = JWTManager()
def get_session():
    return Session(bind=db.engine)