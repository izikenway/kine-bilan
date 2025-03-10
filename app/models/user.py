"""
Modèle User pour l'authentification
"""

from datetime import datetime
from app import db
from werkzeug.security import generate_password_hash

class User(db.Model):
    """Modèle pour les utilisateurs de l'application"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    role = db.Column(db.String(20), default='user')  # 'admin' ou 'user'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __init__(self, email, password, name, role='user'):
        self.email = email
        self.password = generate_password_hash(password)
        self.name = name
        self.role = role
    
    def __repr__(self):
        return f'<User {self.email}>'