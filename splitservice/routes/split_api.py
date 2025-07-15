from flask import Blueprint, request, jsonify
from splitservice.models.split import SplitInvoiceDetail, SplitInvoiceUser
from extensions import db  # or get_session()

split_api = Blueprint('split_api', __name__)

@split_api.route('/api/splits/<bill_id>', methods=['GET'])
def get_split_details(bill_id):
    user_id = request.args.get('user_id')
    if not user_id:
        return jsonify({'error': 'Missing user_id'}), 400

    session = db.session
    try:
        details = session.query(SplitInvoiceDetail).filter_by(userid=user_id, billId=bill_id).all()
        users = session.query(SplitInvoiceUser).filter_by(userid=user_id).all()
        email_to_name = {u.email: u.name for u in users}

        # Group shared_with names by item
        split_map = {}
        for d in details:
            split_map.setdefault(d.item, []).append(email_to_name.get(d.shared_with, d.shared_with))

        return jsonify(split_map)
    except Exception as e:
        return jsonify({'error': str(e)}), 500
