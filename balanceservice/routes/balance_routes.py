from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy import func
from balanceservice.models.balance import DebtSummary, SettlementLog, SplitInvoiceUser
from extensions import db
import logging

balance_bp = Blueprint("balance", __name__)
logger = logging.getLogger(__name__)

@balance_bp.route("/api/balances", methods=["GET"])
@jwt_required()
def get_balances():
    user = get_jwt_identity()
    user_email = user.get("username")

    try:
        total_borrowed = db.session.query(func.coalesce(func.sum(DebtSummary.total_amount), 0)).filter_by(
            owed_by_email=user_email, settled=False).scalar()

        total_owed = db.session.query(func.coalesce(func.sum(DebtSummary.total_amount), 0)).filter_by(
            paid_by_email=user_email, settled=False).scalar()

        owed_details = db.session.query(
            DebtSummary.paid_by_email, func.sum(DebtSummary.total_amount)
        ).filter_by(owed_by_email=user_email, settled=False).group_by(DebtSummary.paid_by_email).all()

        borrowed_details = db.session.query(
            DebtSummary.owed_by_email, func.sum(DebtSummary.total_amount)
        ).filter_by(paid_by_email=user_email, settled=False).group_by(DebtSummary.owed_by_email).all()

        def resolve_names(pairs):
            results = []
            for email, amount in pairs:
                user = SplitInvoiceUser.query.filter_by(email=email).first()
                results.append({
                    "email": email,
                    "name": user.name if user else email,
                    "amount": round(amount, 2)
                })
            return results

        return jsonify({
            "total_money_owed": round(total_owed, 2),
            "total_money_borrowed": round(total_borrowed, 2),
            "owed_details": resolve_names(owed_details),
            "borrowed_details": resolve_names(borrowed_details)
        })

    except Exception as e:
        logger.error(f"Error in /api/balances: {e}")
        return jsonify({"error": "Failed to load balances"}), 500

@balance_bp.route('/my_balances', methods=['GET'])
@jwt_required()
def my_balances():
    try:
        user = get_jwt_identity()
        email = user['username']

        owed_to_me = db.session.query(DebtSummary).filter_by(paid_by_email=email, settled=False).all()
        i_owe = db.session.query(DebtSummary).filter_by(owed_by_email=email, settled=False).all()

        return jsonify({
            'you_are_owed': [{'from': r.owed_by_email, 'amount': r.total_amount - r.settled_amount} for r in owed_to_me],
            'you_owe': [{'to': r.paid_by_email, 'amount': r.total_amount - r.settled_amount} for r in i_owe]
        })
    except Exception as e:
        logger.error(f"Failed in /my_balances: {e}")
        return jsonify({'error': 'Unable to fetch balances', 'details': str(e)}), 500

@balance_bp.route('/owe_to', methods=['GET'])
@jwt_required()
def owe_to():
    try:
        user = get_jwt_identity()
        email = user['username']
        rows = DebtSummary.query.filter_by(owed_by_email=email, settled=False).all()
        return jsonify([{'to': r.paid_by_email, 'amount': r.total_amount - r.settled_amount} for r in rows])
    except Exception as e:
        logger.error(f"Failed in /owe_to: {e}")
        return jsonify({'error': 'Unable to fetch owe_to', 'details': str(e)}), 500

@balance_bp.route('/owed_by', methods=['GET'])
@jwt_required()
def owed_by():
    try:
        user = get_jwt_identity()
        email = user['username']
        rows = DebtSummary.query.filter_by(paid_by_email=email, settled=False).all()
        return jsonify([{'from': r.owed_by_email, 'amount': r.total_amount - r.settled_amount} for r in rows])
    except Exception as e:
        logger.error(f"Failed in /owed_by: {e}")
        return jsonify({'error': 'Unable to fetch owed_by', 'details': str(e)}), 500

@balance_bp.route('/balance_summary', methods=['GET'])
@jwt_required()
def balance_summary():
    try:
        rows = DebtSummary.query.filter_by(settled=False).all()
        return jsonify([{
            'paid_by': r.paid_by_email,
            'owed_by': r.owed_by_email,
            'total_amount': r.total_amount,
            'settled_amount': r.settled_amount,
            'net_due': r.total_amount - r.settled_amount
        } for r in rows])
    except Exception as e:
        logger.error(f"Failed in /balance_summary: {e}")
        return jsonify({'error': 'Unable to fetch summary', 'details': str(e)}), 500

@balance_bp.route("/api/settlement_history", methods=["GET"])
@jwt_required()
def get_settlement_history():
    try:
        logs = SettlementLog.query.order_by(SettlementLog.timestamp.desc()).limit(50).all()
        return jsonify([{
            "paid_by": l.paid_by_email,
            "owed_by": l.owed_by_email,
            "amount": l.amount_paid,
            "method": l.method,
            "note": l.note,
            "timestamp": l.timestamp.isoformat()
        } for l in logs])
    except Exception as e:
        logger.error(f"Failed in /api/settlement_history: {e}")
        return jsonify({"error": "Failed to load history"}), 500
