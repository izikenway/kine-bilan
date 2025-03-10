"""
Routes d'authentification
"""

from flask import request, jsonify
from flask_jwt_extended import create_access_token, create_refresh_token, jwt_required, get_jwt_identity
from app.api import api_bp
from app import db
from app.models.user import User
from werkzeug.security import check_password_hash

@api_bp.route('/auth/login', methods=['POST'])
def login():
    """Authentification de l'utilisateur"""
    if not request.is_json:
        return jsonify({"message": "Format JSON requis"}), 400
    
    data = request.get_json()
    email = data.get('email', None)
    password = data.get('password', None)
    
    if not email or not password:
        return jsonify({"message": "Email et mot de passe requis"}), 400
    
    user = User.query.filter_by(email=email).first()
    
    if not user or not check_password_hash(user.password, password):
        return jsonify({"message": "Email ou mot de passe incorrect"}), 401
    
    access_token = create_access_token(identity=user.id)
    refresh_token = create_refresh_token(identity=user.id)
    
    return jsonify(
        access_token=access_token,
        refresh_token=refresh_token,
        user={
            'id': user.id,
            'email': user.email,
            'name': user.name,
            'role': user.role
        }
    ), 200

@api_bp.route('/auth/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    """Rafraîchissement du token d'accès"""
    current_user_id = get_jwt_identity()
    new_access_token = create_access_token(identity=current_user_id)
    
    return jsonify(access_token=new_access_token), 200

@api_bp.route('/auth/me', methods=['GET'])
@jwt_required()
def me():
    """Récupération des informations de l'utilisateur connecté"""
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    
    if not user:
        return jsonify({"message": "Utilisateur non trouvé"}), 404
    
    return jsonify(
        id=user.id,
        email=user.email,
        name=user.name,
        role=user.role
    ), 200