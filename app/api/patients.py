"""
Routes API pour la gestion des patients
"""

from flask import request, jsonify
from flask_jwt_extended import jwt_required
from app.api import api_bp
from app import db
from app.models.patient import Patient
from datetime import datetime

@api_bp.route('/patients', methods=['GET'])
@jwt_required()
def get_patients():
    """Récupérer la liste des patients"""
    # Paramètres de pagination et filtrage
    page = request.args.get('page', 1, type=int)
    per_page = min(request.args.get('per_page', 20, type=int), 100)
    search = request.args.get('search', '')
    needs_bilan = request.args.get('needs_bilan', None)
    
    # Construction de la requête
    query = Patient.query
    
    # Filtrer par nom/prénom si recherche
    if search:
        search_term = f"%{search}%"
        query = query.filter(
            (Patient.first_name.ilike(search_term)) | 
            (Patient.last_name.ilike(search_term)) |
            (Patient.email.ilike(search_term))
        )
    
    # Filtrer les patients qui ont besoin d'un bilan
    if needs_bilan == 'true':
        max_days = int(request.args.get('max_days', 60))
        today = datetime.utcnow().date()
        
        # Patients sans date de bilan ou dont le dernier bilan est trop ancien
        query = query.filter(
            (Patient.last_bilan_date == None) | 
            ((today - Patient.last_bilan_date) >= max_days)
        )
    
    # Pagination
    paginated_patients = query.order_by(Patient.last_name, Patient.first_name).paginate(page=page, per_page=per_page)
    
    return jsonify({
        'patients': [patient.to_dict() for patient in paginated_patients.items],
        'total': paginated_patients.total,
        'pages': paginated_patients.pages,
        'current_page': page
    })

@api_bp.route('/patients/<int:patient_id>', methods=['GET'])
@jwt_required()
def get_patient(patient_id):
    """Récupérer les détails d'un patient"""
    patient = Patient.query.get_or_404(patient_id)
    return jsonify(patient.to_dict())

@api_bp.route('/patients', methods=['POST'])
@jwt_required()
def create_patient():
    """Créer un nouveau patient"""
    if not request.is_json:
        return jsonify({"message": "Format JSON requis"}), 400
    
    data = request.get_json()
    
    # Validation des données
    if not data.get('first_name') or not data.get('last_name'):
        return jsonify({"message": "Le prénom et le nom sont requis"}), 400
    
    # Vérifier si l'email est unique s'il est fourni
    if data.get('email'):
        existing_patient = Patient.query.filter_by(email=data.get('email')).first()
        if existing_patient:
            return jsonify({"message": "Un patient avec cet email existe déjà"}), 409
    
    # Conversion de la date de naissance si fournie
    birth_date = None
    if data.get('birth_date'):
        try:
            birth_date = datetime.fromisoformat(data.get('birth_date')).date()
        except ValueError:
            return jsonify({"message": "Format de date de naissance invalide. Utilisez ISO 8601 (YYYY-MM-DD)"}), 400
    
    # Conversion de la date du dernier bilan si fournie
    last_bilan_date = None
    if data.get('last_bilan_date'):
        try:
            last_bilan_date = datetime.fromisoformat(data.get('last_bilan_date')).date()
        except ValueError:
            return jsonify({"message": "Format de date de dernier bilan invalide. Utilisez ISO 8601 (YYYY-MM-DD)"}), 400
    
    # Création du patient
    patient = Patient(
        first_name=data.get('first_name'),
        last_name=data.get('last_name'),
        email=data.get('email'),
        phone=data.get('phone'),
        birth_date=birth_date,
        address=data.get('address'),
        medical_condition=data.get('medical_condition'),
        doctolib_id=data.get('doctolib_id'),
        notes=data.get('notes'),
        last_bilan_date=last_bilan_date
    )
    
    db.session.add(patient)
    db.session.commit()
    
    return jsonify(patient.to_dict()), 201

@api_bp.route('/patients/<int:patient_id>', methods=['PUT'])
@jwt_required()
def update_patient(patient_id):
    """Mettre à jour un patient existant"""
    if not request.is_json:
        return jsonify({"message": "Format JSON requis"}), 400
    
    patient = Patient.query.get_or_404(patient_id)
    data = request.get_json()
    
    # Mise à jour des champs simples
    if 'first_name' in data:
        patient.first_name = data['first_name']
    if 'last_name' in data:
        patient.last_name = data['last_name']
    if 'email' in data:
        # Vérifier l'unicité de l'email si changé
        if data['email'] and data['email'] != patient.email:
            existing_patient = Patient.query.filter_by(email=data['email']).first()
            if existing_patient and existing_patient.id != patient_id:
                return jsonify({"message": "Un patient avec cet email existe déjà"}), 409
        patient.email = data['email']
    if 'phone' in data:
        patient.phone = data['phone']
    if 'address' in data:
        patient.address = data['address']
    if 'medical_condition' in data:
        patient.medical_condition = data['medical_condition']
    if 'doctolib_id' in data:
        patient.doctolib_id = data['doctolib_id']
    if 'notes' in data:
        patient.notes = data['notes']
    
    # Traitement de la date de naissance
    if 'birth_date' in data:
        if data['birth_date']:
            try:
                patient.birth_date = datetime.fromisoformat(data['birth_date']).date()
            except ValueError:
                return jsonify({"message": "Format de date de naissance invalide. Utilisez ISO 8601 (YYYY-MM-DD)"}), 400
        else:
            patient.birth_date = None
    
    # Traitement de la date du dernier bilan
    if 'last_bilan_date' in data:
        if data['last_bilan_date']:
            try:
                patient.last_bilan_date = datetime.fromisoformat(data['last_bilan_date']).date()
            except ValueError:
                return jsonify({"message": "Format de date de dernier bilan invalide. Utilisez ISO 8601 (YYYY-MM-DD)"}), 400
        else:
            patient.last_bilan_date = None
    
    db.session.commit()
    
    return jsonify(patient.to_dict())

@api_bp.route('/patients/<int:patient_id>', methods=['DELETE'])
@jwt_required()
def delete_patient(patient_id):
    """Supprimer un patient"""
    patient = Patient.query.get_or_404(patient_id)
    
    db.session.delete(patient)
    db.session.commit()
    
    return jsonify({"message": "Patient supprimé avec succès"}), 200

@api_bp.route('/patients/needs-bilan', methods=['GET'])
@jwt_required()
def get_patients_needing_bilan():
    """Récupérer la liste des patients ayant besoin d'un bilan"""
    max_days = int(request.args.get('max_days', 60))
    today = datetime.utcnow().date()
    
    patients = Patient.query.filter(
        (Patient.last_bilan_date == None) | 
        ((today - Patient.last_bilan_date) >= max_days)
    ).order_by(Patient.last_name, Patient.first_name).all()
    
    return jsonify([patient.to_dict() for patient in patients])