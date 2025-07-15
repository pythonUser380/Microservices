import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from splitservice.models.split import db, SplitInvoiceDetail, SplitInvoiceUser
from splitservice.models.groceries_reflect import get_session, models as ref_models
import logging


split_bp = Blueprint('split', __name__)
logger = logging.getLogger(__name__)

@split_bp.route('/add_split_user', methods=['POST'])
@jwt_required()
def add_split_user():
    try:
        user = get_jwt_identity()
        data = request.get_json()
        email = data.get('email')
        name = data.get('name')

        if not email or not name:
            logger.warning("Missing name or email in request")
            return jsonify({'error': 'Missing name or email'}), 400

        existing = SplitInvoiceUser.query.filter_by(userid=user['id'], email=email).first()
        if existing:
            logger.info(f"Split user {email} already exists for user {user['id']}")
            return jsonify({'message': 'User already exists'}), 200

        new_user = SplitInvoiceUser(name=name, email=email, userid=user['id'])
        db.session.add(new_user)
        db.session.commit()
        logger.info(f"Added new split user {email} for user {user['id']}")
        return jsonify({'message': 'Split user added successfully'})

    except Exception as e:
        logger.error(f"Failed to add split user: {e}")
        return jsonify({'error': 'Failed to add user', 'details': str(e)}), 500


@split_bp.route('/my_split_users', methods=['GET'])
@jwt_required()
def my_split_users():
    try:
        user = get_jwt_identity()
        users = SplitInvoiceUser.query.filter_by(userid=user['id']).all()
        logger.info(f"Fetched {len(users)} split users for user {user['id']}")
        return jsonify([
            {'name': u.name, 'email': u.email} for u in users
        ])
    except Exception as e:
        logger.error(f"Failed to fetch split users: {e}")
        return jsonify({'error': 'Failed to fetch split users', 'details': str(e)}), 500


@split_bp.route('/split_invoice', methods=['POST'])
@jwt_required()
def split_invoice():
    try:
        user = get_jwt_identity()
        data = request.get_json()

        bill_id = data.get('billId')
        items = data.get('items')

        if not bill_id or not items:
            logger.warning("Missing billId or items in request")
            return jsonify({'error': 'Missing billId or items'}), 400

        groceries = ref_models.get('groceries')
        if not groceries:
            logger.error("groceries table not available")
            return jsonify({'error': 'groceries table not available'}), 500

        with get_session() as session:
            invoice_items = session.query(groceries).filter_by(userid=user['id'], billId=bill_id).all()
            valid_item_names = {item.item.lower() for item in invoice_items}

        saved = 0
        for entry in items:
            item = entry.get('item', '').lower()
            shared_with = entry.get('shared_with')
            amount = entry.get('amount')

            if not item or not shared_with or amount is None:
                logger.warning(f"Skipping invalid entry: {entry}")
                continue

            if item not in valid_item_names:
                logger.warning(f"Item '{item}' not found in groceries for user {user['id']} and bill {bill_id}")
                continue

            detail = SplitInvoiceDetail(
                billId=bill_id,
                item=item,
                shared_with=','.join(shared_with),
                amount=amount,
                userid=user['id']
            )
            db.session.add(detail)
            saved += 1

        db.session.commit()
        logger.info(f"Saved {saved} split entries for bill {bill_id} and user {user['id']}")
        return jsonify({'message': f'{saved} items split successfully'})

    except Exception as e:
        logger.error(f"Failed to split invoice: {e}")
        return jsonify({'error': 'Split failed', 'details': str(e)}), 500


@split_bp.route('/split_invoice/<bill_id>', methods=['GET'])
@jwt_required()
def get_split_details(bill_id):
    try:
        user = get_jwt_identity()
        splits = SplitInvoiceDetail.query.filter_by(userid=user['id'], billId=bill_id).all()
        logger.info(f"Fetched {len(splits)} split details for bill {bill_id} and user {user['id']}")
        return jsonify([
            {
                'item': s.item,
                'shared_with': s.shared_with.split(',') if s.shared_with else [],
                'amount': s.amount
            } for s in splits
        ])
    except Exception as e:
        logger.error(f"Failed to get split details for bill {bill_id}: {e}")
        return jsonify({'error': 'Failed to fetch split details', 'details': str(e)}), 500

@split_bp.route("/api/split_users", methods=["GET"])
def get_split_users():
    userid = request.args.get("userid")
    if not userid:
        return jsonify({"error": "Missing userid"}), 400

    try:
        users = SplitInvoiceUser.query.filter_by(userid=userid).all()
        result = [
            {
                "email": user.email,
                "name": user.name,
                "billId": user.billId
            } for user in users
        ]
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@split_bp.route("/api/split_items/<bill_id>", methods=["GET"])
def get_split_items(bill_id):
    userid = request.args.get("userid")
    if not userid:
        return jsonify({"error": "Missing userid"}), 400

    try:
        details = SplitInvoiceDetail.query.filter_by(userid=userid, billId=bill_id).all()
        result = {}

        for detail in details:
            result.setdefault(detail.item, []).append(detail.shared_with)

        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500