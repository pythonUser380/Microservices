from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from settlementservice.models.settlement import db, DebtSettlements, DebtSettlementsBills, DebtSummary, SettlementLog,Settlements
from datetime import datetime
from sqlalchemy import func

settlement_bp = Blueprint('settlement', __name__)

@settlement_bp.route('/settle', methods=['POST'])
@jwt_required()
def settle_debt():
    user = get_jwt_identity()
    data = request.get_json()

    paid_by = data.get('paid_by_email')
    owed_by = data.get('owed_by_email')
    amount = float(data.get('amount', 0))
    method = data.get('method', 'unknown')
    note = data.get('note', '')

    if not paid_by or not owed_by or amount <= 0:
        return jsonify({'error': 'Invalid settlement data'}), 400

    try:
        # Log the settlement
        log = SettlementLog(
            paid_by_email=paid_by,
            owed_by_email=owed_by,
            amount_paid=amount,
            method=method,
            note=note,
            timestamp=datetime.utcnow()
        )
        db.session.add(log)

        # Update summary
        summary = DebtSummary.query.filter_by(paid_by_email=paid_by, owed_by_email=owed_by).first()
        if summary:
            summary.settled_amount += amount
            summary.last_settled_on = datetime.utcnow()
            summary.num_partial_settlements += 1
            if summary.settled_amount >= summary.total_amount:
                summary.settled = True
        else:
            return jsonify({'error': 'No debt summary found'}), 404

        db.session.commit()
        return jsonify({'message': 'Settlement recorded'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Settlement failed', 'details': str(e)}), 500


@settlement_bp.route('/debts', methods=['GET'])
@jwt_required()
def view_debts():
    user = get_jwt_identity()
    debts = DebtSettlements.query.filter_by(userid=user['id'], settled=False).all()
    return jsonify([
        {
            'billId': d.billId,
            'paid_by_email': d.paid_by_email,
            'owed_by_email': d.owed_by_email,
            'amount': d.amount,
            'settled': d.settled
        } for d in debts
    ])


@settlement_bp.route('/settlement_log', methods=['GET'])
@jwt_required()
def settlement_log():
    logs = SettlementLog.query.order_by(SettlementLog.timestamp.desc()).limit(50).all()
    return jsonify([
        {
            'paid_by': l.paid_by_email,
            'owed_by': l.owed_by_email,
            'amount': l.amount_paid,
            'method': l.method,
            'note': l.note,
            'timestamp': l.timestamp
        } for l in logs
    ])


@settlement_bp.route('/summary', methods=['GET'])
@jwt_required()
def summary():
    user = get_jwt_identity()
    rows = DebtSummary.query.filter_by(settled=False).all()
    return jsonify([
        {
            'paid_by': r.paid_by_email,
            'owed_by': r.owed_by_email,
            'total': r.total_amount,
            'settled': r.settled,
            'partial_paid': r.settled_amount
        } for r in rows
    ])

@settlement_bp.route("/api/settlements/<int:settlement_id>/toggle", methods=["PATCH"])
def toggle_settled(settlement_id):
    try:
        row = Settlements.query.get(settlement_id)
        if not row:
            return jsonify({"error": "Settlement not found"}), 404

        row.settled = not row.settled
        db.session.commit()
        return jsonify({"message": "Toggled", "settled": row.settled}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


#--------------------------------------------------------------------
#  APIs used by splitservice or internal tools
# --------------------------------------------------------------------

@settlement_bp.route("/api/settlements", methods=["POST"])
def store_settlement():
    try:
        data = request.get_json()
        settlement = Settlements(**data)
        db.session.add(settlement)
        db.session.commit()
        return jsonify({"message": "Settlement saved"}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


@settlement_bp.route("/api/debts/bills", methods=["POST"])
def store_debt_summary():
    try:
        data = request.get_json()
        summary = DebtSettlementsBills(**data)
        db.session.add(summary)
        db.session.commit()
        return jsonify({"message": "Debt summary saved"}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


@settlement_bp.route("/api/debts/<bill_id>", methods=["GET"])
def get_debt_summary(bill_id):
    user_id = request.args.get("user_id")
    if not user_id:
        return jsonify({"error": "Missing user_id"}), 400

    try:
        rows = DebtSettlementsBills.query.filter_by(billId=bill_id, user_id=user_id).all()
        return jsonify([
            {"friend": r.friend_email, "amount": r.amount}
            for r in rows
        ])
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@settlement_bp.route("/api/settlements", methods=["DELETE"])
def delete_settlements_for_bill():
    bill_id = request.args.get("bill_id")
    user_id = request.args.get("user_id")
    if not bill_id or not user_id:
        return jsonify({"error": "Missing bill_id or user_id"}), 400

    try:
        Settlements.query.filter_by(billId=bill_id, userid=user_id).delete()
        DebtSettlementsBills.query.filter_by(billId=bill_id, user_id=user_id).delete()
        db.session.commit()
        return jsonify({"message": "Deleted settlements"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


@settlement_bp.route("/api/debts/recalculate", methods=["POST"])
def recalculate_debt_summary():
    try:
        data = request.get_json()
        user_id = data.get("user_id")
        bill_id = data.get("bill_id")

        if not user_id or not bill_id:
            return jsonify({"error": "Missing bill_id or user_id"}), 400

        DebtSettlementsBills.query.filter_by(billId=bill_id, user_id=user_id).delete()

        results = db.session.query(
            Settlements.owed_by_email,
            func.sum(Settlements.amount)
        ).filter_by(userid=user_id, billId=bill_id).group_by(Settlements.owed_by_email).all()

        for email, amount in results:
            summary = DebtSettlementsBills(
                user_id=user_id,
                friend_email=email,
                billId=bill_id,
                amount=round(amount, 2)
            )
            db.session.add(summary)

        db.session.commit()
        return jsonify({"message": "Recalculated summary"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500
