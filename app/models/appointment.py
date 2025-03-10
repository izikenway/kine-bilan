"""
Modèle pour les rendez-vous
"""

from datetime import datetime
from app import db

class Appointment(db.Model):
    """Modèle pour les rendez-vous de kinésithérapie"""
    __tablename__ = 'appointments'
    
    id = db.Column(db.Integer, primary_key=True)
    doctolib_id = db.Column(db.String(100), unique=True, nullable=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patients.id'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    time = db.Column(db.Time, nullable=False)
    duration = db.Column(db.Integer, default=30)  # durée en minutes
    status = db.Column(db.String(20), default='scheduled')  # scheduled, completed, cancelled, missed
    type = db.Column(db.String(50), nullable=False)  # regular, bilan
    notes = db.Column(db.Text, nullable=True)
    is_bilan = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __init__(self, patient_id, date, time, duration=30, status='scheduled', 
                 type='regular', notes=None, is_bilan=False, doctolib_id=None):
        self.patient_id = patient_id
        self.date = date
        self.time = time
        self.duration = duration
        self.status = status
        self.type = type
        self.notes = notes
        self.is_bilan = is_bilan
        self.doctolib_id = doctolib_id
    
    def __repr__(self):
        return f'<Appointment {self.date} {self.time}>'
    
    def to_dict(self):
        """Convertir en dictionnaire pour l'API"""
        return {
            'id': self.id,
            'doctolib_id': self.doctolib_id,
            'patient_id': self.patient_id,
            'date': self.date.isoformat(),
            'time': self.time.isoformat(),
            'datetime': datetime.combine(self.date, self.time).isoformat(),
            'duration': self.duration,
            'status': self.status,
            'type': self.type,
            'notes': self.notes,
            'is_bilan': self.is_bilan,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }
    
    @classmethod
    def get_upcoming_for_patient(cls, patient_id):
        """Récupérer les prochains rendez-vous d'un patient"""
        now = datetime.utcnow()
        today = now.date()
        current_time = now.time()
        
        # Filtrer les rendez-vous aujourd'hui et à venir
        return cls.query.filter(
            (cls.patient_id == patient_id) &
            ((cls.date > today) | ((cls.date == today) & (cls.time > current_time))) &
            (cls.status == 'scheduled')
        ).order_by(cls.date, cls.time).all()
    
    @classmethod
    def update_bilan_status(cls, appointment_id, is_bilan=True):
        """Marquer un rendez-vous comme bilan"""
        appointment = cls.query.get(appointment_id)
        if appointment:
            appointment.is_bilan = is_bilan
            appointment.type = 'bilan' if is_bilan else 'regular'
            db.session.commit()
            
            # Mettre à jour la date du dernier bilan du patient
            if is_bilan:
                from app.models.patient import Patient
                patient = Patient.query.get(appointment.patient_id)
                if patient:
                    patient.last_bilan_date = appointment.date
                    db.session.commit()
            
            return True
        return False