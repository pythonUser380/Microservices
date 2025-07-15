from flask import Blueprint, request, jsonify
from settlementservice.models.settlement import DebtSettlementsBills
from settlementservice.extensions import db

debt_api = Blueprint('debt_api', __name__)

@debt_api.route('/api/debts/<bill_id>', methods=['GET'])
def get_debts_for_bill(bill_id):
    user_id = request.args.get('user_id')
    if not user_id:
        return jsonify({'error': 'Missing user_id'}), 400

    try:
        debts = db.session.query(DebtSettlementsBills).filter_by(billId=bill_id, created_by=user_id).all()
        response = [
            {
                "paid_by": d.paid_by_email,
                "owed_by": d.owed_by_email,
                "amount": round(d.amount, 2)
            } for d in debts
        ]
        return jsonify(response)
    except Exception as e:
        return jsonify({'error': str(e)}), 500
