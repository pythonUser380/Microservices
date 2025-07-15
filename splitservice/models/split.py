from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from sqlalchemy import Column, Integer, String, ForeignKey

# This would normally be imported from splitservice.extensions
db = SQLAlchemy()

class SplitInvoiceUser(db.Model):
    __tablename__ = 'SplitInvoiceUsers'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    email = db.Column(db.String(100), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    userid = db.Column(db.Integer, nullable=False)     # Link to USERDATA in auth service
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)


class SplitInvoiceDetail(db.Model):
    __tablename__ = 'SplitInvoiceDetail'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    billId = db.Column(db.String(100), nullable=False)
    item = db.Column(db.String(100), nullable=False)
    shared_with = db.Column(db.String(255), nullable=False)  # Comma-separated emails
    amount = db.Column(db.Float, nullable=False)
    userid = db.Column(db.Integer, nullable=False)  # Creator ID
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

__all__ = ['db', 'SplitInvoiceDetail', 'SplitInvoiceUser']