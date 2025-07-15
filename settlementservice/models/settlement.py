from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class DebtSettlements(db.Model):
    __tablename__ = 'DebtSettlements'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    paid_by_email = db.Column(db.String(100), nullable=False)
    owed_by_email = db.Column(db.String(100), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    settled = db.Column(db.Boolean, default=False)
    userid = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)


class DebtSettlementsBills(db.Model):
    __tablename__ = 'DebtSettlementsBills'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    billId = db.Column(db.String(100), nullable=False)
    paid_by_email = db.Column(db.String(100), nullable=False)
    owed_by_email = db.Column(db.String(100), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    settled = db.Column(db.Boolean, default=False)
    created_by = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)


class DebtSummary(db.Model):
    __tablename__ = 'DebtSummary'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    paid_by_email = db.Column(db.String(255), nullable=False)
    owed_by_email = db.Column(db.String(255), nullable=False)
    total_amount = db.Column(db.Float(10, 2), nullable=False)
    original_amount = db.Column(db.Float(10, 2), nullable=False, default=0.0)
    settled_amount = db.Column(db.Float(10, 2), nullable=False, default=0.0)
    last_updated = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    last_settled_on = db.Column(db.DateTime, nullable=True)
    num_partial_settlements = db.Column(db.Integer, default=0)
    notes = db.Column(db.String(100), nullable=True)
    settled = db.Column(db.Boolean, default=False)


class SettlementLog(db.Model):
    __tablename__ = 'SettlementLog'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    paid_by_email = db.Column(db.String(255), nullable=False)
    owed_by_email = db.Column(db.String(255), nullable=False)
    amount_paid = db.Column(db.Float(10, 2), nullable=False)
    method = db.Column(db.String(100), nullable=True)
    note = db.Column(db.String(100), nullable=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

class Settlements(db.Model):
    __tablename__ = 'settlements'

    id = db.Column(db.Integer, primary_key=True)
    billId = db.Column(db.String(50), nullable=False)
    paid_by = db.Column(db.Integer, nullable=False)             # user ID of payer
    owed_by = db.Column(db.Integer, nullable=False)             # user ID of debtor
    paid_by_email = db.Column(db.String(100), nullable=False)
    owed_by_email = db.Column(db.String(100), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    settled = db.Column(db.Boolean, default=False)
    userid = db.Column(db.Integer, nullable=False)              # who created the split (logged-in user)

    def __repr__(self):
        return f"<Settlement bill={self.billId} paid_by={self.paid_by_email} owed_by={self.owed_by_email} amount={self.amount}>"