from flask import Blueprint, request, jsonify, render_template, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from utils.parser_helpers import create_dataframe
from utils.date_utils import convert_date
from datetime import datetime
import os
import logging
from flask import Blueprint, render_template, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from invoiceservice.extensions import db, get_session
import requests
import logging
from invoiceservice.models.invoice import Grocery


invoice_bp = Blueprint('invoice', __name__)
logger = logging.getLogger(__name__)


UPLOAD_FOLDER = "static/uploads"
ALLOWED_EXTENSIONS = {'pdf'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def sanitize_input(value):
    return value.isalnum() or all(c.isalnum() or c in ('_', '-', '.') for c in value)

@invoice_bp.route('/upload', methods=['POST'])
@jwt_required()
def upload_invoice():
    try:
        user = get_jwt_identity()
        user_id = user['id']

        filename = request.form.get('filename')
        if not filename:
            return jsonify({'error': 'Missing filename'}), 400

        if not filename.lower().endswith('.pdf'):
            filename += '.pdf'

        shop = request.form.get('NameOfTheShop')
        month = request.form.get('month')
        year = request.form.get('year')
        file = request.files.get('file')

        if not all([shop, month, year, file]):
            return jsonify({'error': 'Missing required fields'}), 400

        if not sanitize_input(filename + shop + month + year):
            return jsonify({'error': 'Invalid characters in input'}), 400

        if not allowed_file(file.filename):
            return jsonify({'error': 'Only PDF files are allowed'}), 400

        # Save file
        upload_dir = os.path.join(UPLOAD_FOLDER, year, month)
        os.makedirs(upload_dir, exist_ok=True)
        pdf_path = os.path.join(upload_dir, filename)
        file.save(pdf_path)

        # Check for duplicate
        groceries = Grocery
        if not groceries:
            return jsonify({'error': 'groceries model not available'}), 500

        with get_session() as session:
            existing = session.query(groceries).filter_by(userid=user_id, billId=filename).count()
            if existing > 0:
                return jsonify({'warning': 'Bill already exists', 'Bill_exists': True}), 200

            df = create_dataframe(pdf_path, filename, month, year, shop.lower(), user_id)
            if df.empty:
                return jsonify({'warning': 'No data extracted from PDF'}), 200

            df['date'] = df['date'].apply(convert_date)

            for _, row in df.iterrows():
                entry = groceries(
                    userid=user_id,
                    billId=filename,
                    month=row['month'],
                    year=int(row['year']),
                    item=row['item'],
                    quantity=row['quantity'],
                    price=row['price'],
                    shopName=row['shopName'],
                    address=row['address'],
                    invoiceNumber=row['invoiceNumber'],
                    totalSum=row['totalSum'],
                    date=row['date']
                )
                session.add(entry)
            session.commit()

        return jsonify({'success': True, 'message': 'Invoice uploaded successfully'})

    except Exception as e:
        logger.error(f"Upload failed: {e}")
        return jsonify({'error': 'Upload failed', 'details': str(e)}), 500


@invoice_bp.route('/check_filename', methods=['POST'])
@jwt_required()
def check_filename():
    try:
        user = get_jwt_identity()
        user_id = user['id']
        filename = request.form.get('filename')

        if not filename:
            return jsonify({'error': 'Missing filename'}), 400

        groceries = Grocery
        if not groceries:
            return jsonify({'error': 'groceries model not available'}), 500

        with get_session() as session:
            exists = session.query(groceries).filter_by(userid=user_id, billId=filename).first() is not None
        return jsonify({'exists': exists})

    except Exception as e:
        logger.error(f"Filename check failed: {e}")
        return jsonify({'error': 'Check failed', 'details': str(e)}), 500

@invoice_bp.route('/view_invoices_by_month', methods=['GET'])
@jwt_required()
def view_by_month():
    try:
        user = get_jwt_identity()
        user_id = user['id']
        month = request.args.get('month')
        year = request.args.get('year')

        #groceries = models.get("groceries")
        groceries = Grocery
        if not groceries:
            return jsonify({'error': 'groceries model not available'}), 500

        with get_session() as session:
            invoices = session.query(groceries).filter_by(userid=user_id, month=month, year=year).all()

            bills = []
            for inv in invoices:
                pdf_url = f"/static/uploads/{inv.year}/{inv.month}/{inv.billId}"
                bills.append({
                    "billId": inv.billId,
                    "shop": inv.shopName,
                    "date": inv.date,
                    "total": inv.totalSum,
                    "pdf_url": pdf_url
                })

        return render_template("view_invoices_month.html", bills=bills, month=month, year=year)

    except Exception as e:
        logger.error(f"Error viewing invoices: {e}")
        return render_template("view_invoices_month.html", bills=[], month=month, year=year, error=str(e))


@invoice_bp.route('/view_data_by_date', methods=['GET'])
@jwt_required()
def view_data_by_date():
    try:
        user = get_jwt_identity()
        user_id = user['id']
        selected_date = request.args.get('date')

        #groceries = models.get("groceries")
        groceries = Grocery
        if not groceries:
            return jsonify({'error': 'groceries model not available'}), 500

        with get_session() as session:
            record = session.query(groceries).filter_by(userid=user_id, date=selected_date).first()
            if not record:
                return jsonify({'warning': f'No records found for {selected_date}'}), 200

        return jsonify({'redirect': f"/view_data?billId={record.billId}"})

    except Exception as e:
        logger.error(f"View data by date failed: {e}")
        return jsonify({'error': 'View failed', 'details': str(e)}), 500


@invoice_bp.route('/view', methods=['GET'])
@jwt_required()
def view_data():
    try:
        user = get_jwt_identity()
        user_id = user['id']
        bill_id = request.args.get('billId')

        if not bill_id:
            return render_template("view.html", message="Missing bill ID")

        #groceries = models.get("groceries")
        groceries = Grocery
        if not groceries:
            return render_template("view.html", message="Data model not available")

        with get_session() as session:
            records = session.query(groceries).filter_by(userid=user_id, billId=bill_id).all()
            if not records:
                return render_template("view.html", message="No records found.")

            record = records[0]
            items_data = [
                {
                    'item': r.item,
                    'quantity': r.quantity,
                    'price': r.price,
                    'shared_with': ''  # To be filled from split service
                } for r in records
            ]

        # 🔁 Fetch shared_with info from splitservice
        split_map = {}
        try:
            split_resp = requests.get(
                f"http://splitService:5002/api/splits/{bill_id}?user_id={user_id}"
            )
            if split_resp.ok:
                split_map = split_resp.json()
                for item_data in items_data:
                    if item_data['item'] in split_map:
                        item_data['shared_with'] = ", ".join(split_map[item_data['item']])
        except Exception as e:
            logger.warning(f"Split service failed: {e}")

        # 🔁 Fetch debt info from settlementservice
        debt_settlement_details = []
        try:
            settle_resp = requests.get(
                f"http://settlementService:5003/api/debts/{bill_id}?user_id={user_id}"
            )
            if settle_resp.ok:
                debt_settlement_details = settle_resp.json()
        except Exception as e:
            logger.warning(f"Settlement service failed: {e}")

        return render_template(
            "view.html",
            bill_info=record.billId,
            totalSum_info=record.totalSum,
            address_info=record.address,
            ShopName=record.shopName,
            date_info=record.date,
            items_data=items_data,
            selected_date=record.date,
            debt_settlement_details=debt_settlement_details,
            logged_in_user=user
        )

    except Exception as e:
        logger.error(f"View data failed: {e}")
        return render_template("view_data.html", message="Failed to load data.")