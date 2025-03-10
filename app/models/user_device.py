"""
Modèle pour les appareils utilisateurs (notifications push)
"""

from datetime import datetime
from app import db

class UserDevice(db.Model):
    """Modèle pour les appareils utilisateurs pour les notifications push"""
    __tablename__ = 'user_devices'
    
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patients.id'), nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    name = db.Column(db.String(100), nullable=True)
    device_type = db.Column(db.String(20), nullable=False)  # 'android', 'ios', 'web'
    token = db.Column(db.String(255), nullable=False, unique=True)
    active = db.Column(db.Boolean, default=True)
    last_used = db.Column(db.DateTime, default=datetime.utcnow)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __init__(self, token, device_type, patient_id=None, user_id=None, name=None):
        self.token = token
        self.device_type = device_type
        self.patient_id = patient_id
        self.user_id = user_id
        self.name = name
    
    def __repr__(self):
        return f'<UserDevice {self.id} - {self.device_type}>'
    
    def to_dict(self):
        """Convertir en dictionnaire pour l'API"""
        return {
            'id': self.id,
            'patient_id': self.patient_id,
            'user_id': self.user_id,
            'name': self.name,
            'device_type': self.device_type,
            'token': self.token,
            'active': self.active,
            'last_used': self.last_used.isoformat() if self.last_used else None,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }
    
    def update_last_used(self):
        """Mettre à jour la date de dernière utilisation"""
        self.last_used = datetime.utcnow()
        db.session.commit()
    
    def deactivate(self):
        """Désactiver l'appareil"""
        self.active = False
        db.session.commit()
    
    @classmethod
    def register_device(cls, token, device_type, patient_id=None, user_id=None, name=None):
        """Enregistrer un nouvel appareil ou mettre à jour un existant"""
        # Vérifier si l'appareil existe déjà
        device = cls.query.filter_by(token=token).first()
        
        if device:
            # Mettre à jour les informations
            device.device_type = device_type
            device.patient_id = patient_id or device.patient_id
            device.user_id = user_id or device.user_id
            device.name = name or device.name
            device.active = True
            device.last_used = datetime.utcnow()
        else:
            # Créer un nouvel appareil
            device = cls(
                token=token,
                device_type=device_type,
                patient_id=patient_id,
                user_id=user_id,
                name=name
            )
            db.session.add(device)
        
        db.session.commit()
        return device