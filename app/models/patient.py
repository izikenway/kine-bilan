"""
Modèle pour les patients
"""

from datetime import datetime
from app import db

class Patient(db.Model):
    """Modèle pour les patients en kinésithérapie"""
    __tablename__ = 'patients'
    
    id = db.Column(db.Integer, primary_key=True)
    doctolib_id = db.Column(db.String(100), unique=True, nullable=True)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=True)
    phone = db.Column(db.String(20), nullable=True)
    birth_date = db.Column(db.Date, nullable=True)
    address = db.Column(db.String(255), nullable=True)
    medical_condition = db.Column(db.Text, nullable=True)
    notes = db.Column(db.Text, nullable=True)
    last_bilan_date = db.Column(db.Date, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relations
    appointments = db.relationship('Appointment', backref='patient', lazy=True, cascade="all, delete-orphan")
    
    def __init__(self, first_name, last_name, email=None, phone=None, birth_date=None, 
                 address=None, medical_condition=None, doctolib_id=None, notes=None, last_bilan_date=None):
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self.phone = phone
        self.birth_date = birth_date
        self.address = address
        self.medical_condition = medical_condition
        self.doctolib_id = doctolib_id
        self.notes = notes
        self.last_bilan_date = last_bilan_date
    
    def __repr__(self):
        return f'<Patient {self.last_name.upper()} {self.first_name}>'
    
    def to_dict(self):
        """Convertir en dictionnaire pour l'API"""
        return {
            'id': self.id,
            'doctolib_id': self.doctolib_id,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'email': self.email,
            'phone': self.phone,
            'birth_date': self.birth_date.isoformat() if self.birth_date else None,
            'address': self.address,
            'medical_condition': self.medical_condition,
            'notes': self.notes,
            'last_bilan_date': self.last_bilan_date.isoformat() if self.last_bilan_date else None,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }
    
    def needs_bilan(self, max_days=60):
        """Vérifier si le patient a besoin d'un bilan"""
        if not self.last_bilan_date:
            return True
        
        days_since_last_bilan = (datetime.utcnow().date() - self.last_bilan_date).days
        return days_since_last_bilan >= max_days