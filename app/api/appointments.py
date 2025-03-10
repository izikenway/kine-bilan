"""
Routes API pour la gestion des rendez-vous
"""

from flask import request, jsonify
from flask_jwt_extended import jwt_required
from app.api import api_bp
from app import db
from app.models.appointment import Appointment
from app.models.patient import Patient
from app.models.notification import Notification
from datetime import datetime, timedelta

@api_bp.route('/appointments', methods=['GET'])
@jwt_required()
def get_appointments():
    """Récupérer la liste des rendez-vous"""
    # Paramètres de pagination et filtrage
    page = request.args.get('page', 1, type=int)
    per_page = min(request.args.get('per_page', 20, type=int), 100)
    patient_id = request.args.get('patient_id', None, type=int)
    date_from = request.args.get('date_from', None)
    date_to = request.args.get('date_to', None)
    status = request.args.get('status', None)
    is_bilan = request.args.get('is_bilan', None)
    
    # Construction de la requête
    query = Appointment.query
    
    # Filtre par patient
    if patient_id:
        query = query.filter(Appointment.patient_id == patient_id)
    
    # Filtre par période
    if date_from:
        try:
            from_date = datetime.fromisoformat(date_from).date()
            query = query.filter(Appointment.date >= from_date)
        except ValueError:
            return jsonify({"message": "Format de date_from invalide. Utilisez ISO 8601 (YYYY-MM-DD)"}), 400
    
    if date_to:
        try:
            to_date = datetime.fromisoformat(date_to).date()
            query = query.filter(Appointment.date <= to_date)
        except ValueError:
            return jsonify({"message": "Format de date_to invalide. Utilisez ISO 8601 (YYYY-MM-DD)"}), 400
    
    # Filtre par statut
    if status:
        query = query.filter(Appointment.status == status)
    
    # Filtre par type de bilan
    if is_bilan is not None:
        is_bilan_bool = is_bilan.lower() == 'true'
        query = query.filter(Appointment.is_bilan == is_bilan_bool)
    
    # Pagination
    paginated_appointments = query.order_by(Appointment.date.desc(), Appointment.time.desc()).paginate(page=page, per_page=per_page)
    
    # Enrichir les données avec les informations du patient
    result = []
    for appointment in paginated_appointments.items:
        app_dict = appointment.to_dict()
        patient = Patient.query.get(appointment.patient_id)
        if patient:
            app_dict['patient'] = {
                'id': patient.id,
                'name': f"{patient.first_name} {patient.last_name}",
                'email': patient.email,
                'phone': patient.phone
            }
        result.append(app_dict)
    
    return jsonify({
        'appointments': result,
        'total': paginated_appointments.total,
        'pages': paginated_appointments.pages,
        'current_page': page
    })

@api_bp.route('/appointments/<int:appointment_id>', methods=['GET'])
@jwt_required()
def get_appointment(appointment_id):
    """Récupérer les détails d'un rendez-vous"""
    appointment = Appointment.query.get_or_404(appointment_id)
    app_dict = appointment.to_dict()
    
    # Ajouter les infos du patient
    patient = Patient.query.get(appointment.patient_id)
    if patient:
        app_dict['patient'] = {
            'id': patient.id,
            'name': f"{patient.first_name} {patient.last_name}",
            'email': patient.email,
            'phone': patient.phone
        }
    
    return jsonify(app_dict)

@api_bp.route('/appointments', methods=['POST'])
@jwt_required()
def create_appointment():
    """Créer un nouveau rendez-vous"""
    if not request.is_json:
        return jsonify({"message": "Format JSON requis"}), 400
    
    data = request.get_json()
    
    # Validation des données obligatoires
    if not data.get('patient_id') or not data.get('date') or not data.get('time'):
        return jsonify({"message": "Patient, date et heure requis"}), 400
    
    # Vérifier si le patient existe
    patient = Patient.query.get(data.get('patient_id'))
    if not patient:
        return jsonify({"message": "Patient non trouvé"}), 404
    
    # Parsing de la date et l'heure
    try:
        appointment_date = datetime.fromisoformat(data.get('date')).date()
        appointment_time = datetime.fromisoformat(data.get('time')).time()
    except ValueError:
        return jsonify({"message": "Format de date ou heure invalide. Utilisez ISO 8601"}), 400
    
    # Création du rendez-vous
    appointment = Appointment(
        patient_id=data.get('patient_id'),
        date=appointment_date,
        time=appointment_time,
        duration=data.get('duration', 30),
        status=data.get('status', 'scheduled'),
        type=data.get('type', 'regular'),
        notes=data.get('notes'),
        is_bilan=data.get('is_bilan', False),
        doctolib_id=data.get('doctolib_id')
    )
    
    db.session.add(appointment)
    
    # Si c'est un bilan, mettre à jour la date du dernier bilan du patient
    if appointment.is_bilan:
        patient.last_bilan_date = appointment.date
    
    db.session.commit()
    
    return jsonify(appointment.to_dict()), 201

@api_bp.route('/appointments/<int:appointment_id>', methods=['PUT'])
@jwt_required()
def update_appointment(appointment_id):
    """Mettre à jour un rendez-vous"""
    if not request.is_json:
        return jsonify({"message": "Format JSON requis"}), 400
    
    appointment = Appointment.query.get_or_404(appointment_id)
    data = request.get_json()
    
    # Traitement de la date si présente
    if 'date' in data:
        try:
            appointment.date = datetime.fromisoformat(data['date']).date()
        except ValueError:
            return jsonify({"message": "Format de date invalide. Utilisez ISO 8601"}), 400
    
    # Traitement de l'heure si présente
    if 'time' in data:
        try:
            appointment.time = datetime.fromisoformat(data['time']).time()
        except ValueError:
            return jsonify({"message": "Format d'heure invalide. Utilisez ISO 8601"}), 400
    
    # Mise à jour des autres champs
    if 'duration' in data:
        appointment.duration = data['duration']
    if 'status' in data:
        appointment.status = data['status']
    if 'type' in data:
        appointment.type = data['type']
    if 'notes' in data:
        appointment.notes = data['notes']
    if 'doctolib_id' in data:
        appointment.doctolib_id = data['doctolib_id']
    
    # Gestion spéciale pour is_bilan
    if 'is_bilan' in data and data['is_bilan'] != appointment.is_bilan:
        appointment.is_bilan = data['is_bilan']
        
        # Si marqué comme bilan, mettre à jour le patient
        if appointment.is_bilan:
            patient = Patient.query.get(appointment.patient_id)
            if patient:
                patient.last_bilan_date = appointment.date
    
    db.session.commit()
    
    return jsonify(appointment.to_dict())

@api_bp.route('/appointments/<int:appointment_id>', methods=['DELETE'])
@jwt_required()
def delete_appointment(appointment_id):
    """Supprimer un rendez-vous"""
    appointment = Appointment.query.get_or_404(appointment_id)
    
    db.session.delete(appointment)
    db.session.commit()
    
    return jsonify({"message": "Rendez-vous supprimé avec succès"}), 200

@api_bp.route('/appointments/check-bilans', methods=['GET'])
@jwt_required()
def check_bilans():
    """Vérifier quels patients ont besoin de bilans et générer des notifications"""
    max_days = int(request.args.get('max_days', 60))
    today = datetime.utcnow().date()
    
    # Trouver les patients qui ont besoin d'un bilan
    patients_needing_bilan = Patient.query.filter(
        (Patient.last_bilan_date == None) | 
        ((today - Patient.last_bilan_date) >= max_days)
    ).all()
    
    notifications_created = 0
    
    for patient in patients_needing_bilan:
        # Vérifier s'ils ont des rendez-vous programmés
        upcoming_appointments = Appointment.get_upcoming_for_patient(patient.id)
        
        if upcoming_appointments:
            # Convertir le prochain rendez-vous en bilan
            next_appointment = upcoming_appointments[0]
            if not next_appointment.is_bilan:
                next_appointment.is_bilan = True
                next_appointment.type = 'bilan'
                patient.last_bilan_date = next_appointment.date
                
                # Créer une notification
                Notification.create_bilan_reminder(patient, next_appointment)
                notifications_created += 1
        else:
            # Créer une notification pour rappeler au patient de prendre rendez-vous
            Notification.create_bilan_reminder(patient)
            notifications_created += 1
    
    db.session.commit()
    
    return jsonify({
        "patients_checked": len(patients_needing_bilan),
        "notifications_created": notifications_created,
        "message": f"{notifications_created} notifications créées pour {len(patients_needing_bilan)} patients"
    })