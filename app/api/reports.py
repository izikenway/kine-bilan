"""
Routes API pour les rapports et statistiques
"""

from flask import request, jsonify
from flask_jwt_extended import jwt_required
from app.api import api_bp
from app import db
from app.models.patient import Patient
from app.models.appointment import Appointment
from app.models.notification import Notification
from datetime import datetime, timedelta
from sqlalchemy import func, and_, or_, extract

@api_bp.route('/reports/dashboard', methods=['GET'])
@jwt_required()
def dashboard():
    """Récupérer les données pour le tableau de bord principal"""
    today = datetime.utcnow().date()
    
    # Nombre total de patients
    total_patients = Patient.query.count()
    
    # Nombre de patients ayant besoin d'un bilan
    max_days = int(request.args.get('max_days', 60))
    patients_needing_bilan = Patient.query.filter(
        or_(
            Patient.last_bilan_date == None,
            (today - Patient.last_bilan_date) >= max_days
        )
    ).count()
    
    # Rendez-vous aujourd'hui
    today_appointments = Appointment.query.filter(
        Appointment.date == today,
        Appointment.status == 'scheduled'
    ).count()
    
    # Rendez-vous cette semaine
    week_start = today - timedelta(days=today.weekday())
    week_end = week_start + timedelta(days=6)
    week_appointments = Appointment.query.filter(
        Appointment.date.between(week_start, week_end),
        Appointment.status == 'scheduled'
    ).count()
    
    # Notifications en attente
    pending_notifications = Notification.query.filter_by(status='pending').count()
    
    # Bilans programmés à venir
    upcoming_bilans = Appointment.query.filter(
        Appointment.date >= today,
        Appointment.is_bilan == True,
        Appointment.status == 'scheduled'
    ).count()
    
    return jsonify({
        'total_patients': total_patients,
        'patients_needing_bilan': patients_needing_bilan,
        'today_appointments': today_appointments,
        'week_appointments': week_appointments,
        'pending_notifications': pending_notifications,
        'upcoming_bilans': upcoming_bilans
    })

@api_bp.route('/reports/appointments/monthly', methods=['GET'])
@jwt_required()
def monthly_appointments():
    """Récupérer les statistiques mensuelles des rendez-vous"""
    # Paramètres de filtrage
    year = request.args.get('year', datetime.utcnow().year, type=int)
    
    # Récupérer le nombre de rendez-vous par mois
    monthly_stats = db.session.query(
        extract('month', Appointment.date).label('month'),
        func.count(Appointment.id).label('total'),
        func.sum(case((Appointment.status == 'completed', 1), else_=0)).label('completed'),
        func.sum(case((Appointment.status == 'cancelled', 1), else_=0)).label('cancelled'),
        func.sum(case((Appointment.status == 'missed', 1), else_=0)).label('missed'),
        func.sum(case((Appointment.is_bilan == True, 1), else_=0)).label('bilans')
    ).filter(
        extract('year', Appointment.date) == year
    ).group_by(
        extract('month', Appointment.date)
    ).all()
    
    # Formater les résultats
    result = []
    for month, total, completed, cancelled, missed, bilans in monthly_stats:
        result.append({
            'month': month,
            'month_name': datetime(year, int(month), 1).strftime('%B'),
            'total': total,
            'completed': completed or 0,
            'cancelled': cancelled or 0,
            'missed': missed or 0,
            'bilans': bilans or 0
        })
    
    return jsonify(result)

@api_bp.route('/reports/bilans/status', methods=['GET'])
@jwt_required()
def bilan_status():
    """Récupérer les statistiques sur le statut des bilans"""
    # Paramètres
    max_days = int(request.args.get('max_days', 60))
    today = datetime.utcnow().date()
    
    # Total des patients
    total_patients = Patient.query.count()
    
    # Patients avec bilan à jour
    patients_with_valid_bilan = Patient.query.filter(
        Patient.last_bilan_date != None,
        (today - Patient.last_bilan_date) < max_days
    ).count()
    
    # Patients sans bilan ou avec bilan dépassé
    patients_without_valid_bilan = Patient.query.filter(
        or_(
            Patient.last_bilan_date == None,
            (today - Patient.last_bilan_date) >= max_days
        )
    ).count()
    
    # Patients avec bilan programmé
    patients_with_upcoming_bilan = db.session.query(
        Patient.id
    ).join(
        Appointment,
        Patient.id == Appointment.patient_id
    ).filter(
        Appointment.date >= today,
        Appointment.is_bilan == True,
        Appointment.status == 'scheduled',
        or_(
            Patient.last_bilan_date == None,
            (today - Patient.last_bilan_date) >= max_days
        )
    ).distinct().count()
    
    # Patients nécessitant un bilan mais sans rendez-vous programmé
    patients_needing_bilan_without_appointment = patients_without_valid_bilan - patients_with_upcoming_bilan
    
    return jsonify({
        'total_patients': total_patients,
        'patients_with_valid_bilan': patients_with_valid_bilan,
        'patients_without_valid_bilan': patients_without_valid_bilan,
        'patients_with_upcoming_bilan': patients_with_upcoming_bilan,
        'patients_needing_bilan_without_appointment': patients_needing_bilan_without_appointment,
        'valid_bilan_percentage': round((patients_with_valid_bilan / total_patients * 100), 2) if total_patients > 0 else 0
    })

@api_bp.route('/reports/notifications', methods=['GET'])
@jwt_required()
def notification_stats():
    """Récupérer les statistiques des notifications"""
    # Paramètres de filtrage
    days = request.args.get('days', 30, type=int)
    start_date = datetime.utcnow() - timedelta(days=days)
    
    # Total des notifications par type et statut
    notifications_by_type = db.session.query(
        Notification.type,
        Notification.status,
        func.count(Notification.id).label('count')
    ).filter(
        Notification.created_at >= start_date
    ).group_by(
        Notification.type,
        Notification.status
    ).all()
    
    # Formater les résultats
    result = {
        'total': 0,
        'by_type': {},
        'by_status': {
            'sent': 0,
            'pending': 0,
            'failed': 0
        }
    }
    
    for notification_type, status, count in notifications_by_type:
        # Incrémenter le total
        result['total'] += count
        
        # Ajouter au compteur par type
        if notification_type not in result['by_type']:
            result['by_type'][notification_type] = {
                'total': 0,
                'sent': 0,
                'pending': 0,
                'failed': 0
            }
        
        result['by_type'][notification_type]['total'] += count
        result['by_type'][notification_type][status] = count
        
        # Ajouter au compteur par statut
        result['by_status'][status] += count
    
    return jsonify(result)

# Fonction utilitaire pour l'opérateur case when en SQLAlchemy
def case(whens, else_=None):
    """Helper pour créer une clause CASE WHEN en SQLAlchemy"""
    return func.case(whens, else_=else_)