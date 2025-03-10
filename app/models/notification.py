"""
Modèle pour les notifications
"""

from datetime import datetime
from app import db

class Notification(db.Model):
    """Modèle pour les notifications envoyées aux patients"""
    __tablename__ = 'notifications'
    
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patients.id'), nullable=False)
    appointment_id = db.Column(db.Integer, db.ForeignKey('appointments.id'), nullable=True)
    type = db.Column(db.String(20), nullable=False)  # email, sms, push
    subject = db.Column(db.String(255), nullable=True)
    message = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(20), default='pending')  # pending, sent, failed
    error = db.Column(db.Text, nullable=True)
    sent_at = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __init__(self, patient_id, message, type='email', subject=None, appointment_id=None):
        self.patient_id = patient_id
        self.message = message
        self.type = type
        self.subject = subject
        self.appointment_id = appointment_id
    
    def __repr__(self):
        return f'<Notification {self.id} - {self.type}>'
    
    def to_dict(self):
        """Convertir en dictionnaire pour l'API"""
        return {
            'id': self.id,
            'patient_id': self.patient_id,
            'appointment_id': self.appointment_id,
            'type': self.type,
            'subject': self.subject,
            'message': self.message,
            'status': self.status,
            'error': self.error,
            'sent_at': self.sent_at.isoformat() if self.sent_at else None,
            'created_at': self.created_at.isoformat()
        }
    
    def mark_as_sent(self):
        """Marquer la notification comme envoyée"""
        self.status = 'sent'
        self.sent_at = datetime.utcnow()
        db.session.commit()
    
    def mark_as_failed(self, error):
        """Marquer la notification comme échouée"""
        self.status = 'failed'
        self.error = error
        db.session.commit()
    
    @classmethod
    def get_pending(cls):
        """Récupérer les notifications en attente d'envoi"""
        return cls.query.filter_by(status='pending').all()
    
    @classmethod
    def create_bilan_reminder(cls, patient, appointment=None):
        """Créer une notification de rappel de bilan"""
        subject = "Rappel de bilan kinésithérapie"
        message = f"Bonjour {patient.first_name},\n\nNous vous rappelons qu'un bilan est nécessaire pour poursuivre vos séances de kinésithérapie. "
        
        if appointment:
            message += f"Votre prochain rendez-vous du {appointment.date.strftime('%d/%m/%Y')} à {appointment.time.strftime('%H:%M')} sera transformé en séance de bilan."
        else:
            message += "Merci de prendre rendez-vous pour une séance de bilan dès que possible."
        
        message += "\n\nCordialement,\nVotre kinésithérapeute"
        
        notification = cls(
            patient_id=patient.id,
            message=message,
            subject=subject,
            appointment_id=appointment.id if appointment else None,
            type='email'
        )
        
        db.session.add(notification)
        db.session.commit()
        
        return notification