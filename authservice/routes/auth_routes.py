from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from authservice.models.user import User
from werkzeug.security import generate_password_hash, check_password_hash
from authservice.extensions import db

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/signup', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    firstname = data.get('firstname')
    lastname = data.get('lastname')

    if User.query.filter_by(username=username).first():
        return jsonify({'error': 'Username already exists'}), 409

    user = User(
        username=username,
        firstname=firstname,
        lastname=lastname,
        password_hash=generate_password_hash(password)
    )

    try:
        db.session.add(user)
        db.session.commit()
        return jsonify({'message': 'User registered successfully'})
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Registration failed: {str(e)}")
        return jsonify({'error': 'Registration failed'}), 500

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    user = User.query.filter_by(username=username).first()

    if not user or not check_password_hash(user.password_hash, password):
        return jsonify({'error': 'Invalid credentials'}), 401

    access_token = create_access_token(identity={
        'id': user.id,
        'username': user.username,
        'firstname': user.firstname,
        'lastname': user.lastname,
        'is_admin': user.is_admin
    })

    return jsonify({
        'access_token': access_token,
        'user': {
            'id': user.id,
            'username': user.username,
            'firstname': user.firstname,
            'lastname': user.lastname,
            'is_admin': user.is_admin
        }
    })

@auth_bp.route('/profile', methods=['GET'])
@jwt_required()
def profile():
    return jsonify(get_jwt_identity())

@auth_bp.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    return jsonify({'message': 'Logout placeholder – handle via token revocation'})

@auth_bp.route('/settings', methods=['POST'])
@jwt_required()
def change_password():
    user_data = get_jwt_identity()
    user = User.query.get(user_data['id'])

    data = request.get_json()
    new_password = data.get('new_password')
    confirm_password = data.get('confirm_password')

    if not new_password or new_password != confirm_password:
        return jsonify({'error': 'Passwords do not match'}), 400

    user.password_hash = generate_password_hash(new_password)
    db.session.commit()
    return jsonify({'message': 'Password updated successfully'})

@auth_bp.route("/api/users/<int:user_id>", methods=["GET"])
def get_user_by_id(user_id):
    user = db.session.query(User).filter_by(id=user_id).first()
    if not user:
        return jsonify({"error": "User not found"}), 404

    return jsonify({
        "id": user.id,
        "username": user.username,
        "firstname": user.firstname,
        "lastname": user.lastname,
        "is_admin": user.is_admin
    })
