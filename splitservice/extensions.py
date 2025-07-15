from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import Session

db = SQLAlchemy()

def get_session():
    return Session(bind=db.engine)
