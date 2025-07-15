# balanceservice/models/balance.py

from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()
class SplitInvoiceUser(db.Model):
    __tablename__ = 'SplitInvoiceUsers'
    id = Column(Integer, primary_key=True, autoincrement=True)
    email = Column(String(100), unique=True, nullable=False)
    name = Column(String(100), nullable=False)
    userid = Column(Integer, ForeignKey('USERDATA.userid'), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)


class DebtSummary(db.Model):
    __tablename__ = 'DebtSummary'
    id = Column(Integer, primary_key=True, autoincrement=True)
    paid_by_email = Column(String(255), nullable=False)
    owed_by_email = Column(String(255), nullable=False)
    total_amount = Column(Float(10, 2), nullable=False)
    original_amount = Column(Float(10, 2), nullable=False, default=0.0)
    settled_amount = Column(Float(10, 2), nullable=False, default=0.0)
    last_updated = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    last_settled_on = Column(DateTime, nullable=True)
    num_partial_settlements = Column(Integer, default=0)
    notes = Column(String(100), nullable=True)
    settled = Column(Boolean, default=False)

    __table_args__ = ({'sqlite_autoincrement': True},)

    def __repr__(self):
        return (f"<DebtSummary(id={self.id}, paid_by_email={self.paid_by_email}, "
                f"owed_by_email={self.owed_by_email}, total_amount={self.total_amount}, "
                f"settled={self.settled})>")


class SettlementLog(db.Model):
    __tablename__ = 'SettlementLog'
    id = Column(Integer, primary_key=True, autoincrement=True)
    paid_by_email = Column(String(255), nullable=False)
    owed_by_email = Column(String(255), nullable=False)
    amount_paid = Column(Float(10, 2), nullable=False)
    method = Column(String(100), nullable=True)
    note = Column(String(100), nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)

    def __repr__(self):
        return f"<SettlementLog({self.paid_by_email} ← {self.owed_by_email}: {self.amount_paid})>"
