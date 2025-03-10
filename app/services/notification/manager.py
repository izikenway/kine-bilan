"""
Gestionnaire centralisé des notifications
"""

import logging
from app import db
from app.models.notification import Notification
from app.models.patient import Patient
from app.services.notification.email import EmailService
from app.services.notification.sms import SMSService
from app.services.notification.push import PushService
from flask import current_app

logger = logging.getLogger(__name__)

class NotificationManager:
    """Gestionnaire pour envoyer des notifications via différents canaux"""
    
    def __init__(self):
        """Initialisation des services"""
        self.email_service = EmailService()
        self.sms_service = SMSService()
        self.push_service = PushService()
    
    def notify_patient(self, patient_id, message, subject=None, channels=None, appointment_id=None):
        """
        Envoyer une notification à un patient via plusieurs canaux
        
        Args:
            patient_id: ID du patient
            message: Contenu du message
            subject: Sujet du message (pour email)
            channels: Liste des canaux à utiliser ['email', 'sms', 'push'], par défaut tous
            appointment_id: ID du rendez-vous associé (optionnel)
            
        Returns:
            dict: Résultats par canal
        """
        # Vérifier si le patient existe
        patient = Patient.query.get(patient_id)
        if not patient:
            logger.error(f"Patient {patient_id} non trouvé")
            return {'success': False, 'error': f"Patient {patient_id} non trouvé"}
        
        # Canaux par défaut si non spécifiés
        if not channels:
            channels = ['email', 'sms', 'push']
        
        # Créer les notifications pour chaque canal
        notifications = []
        for channel in channels:
            notification = Notification(
                patient_id=patient_id,
                message=message,
                subject=subject,
                type=channel,
                appointment_id=appointment_id
            )
            db.session.add(notification)
            notifications.append(notification)
        
        db.session.commit()
        
        # Traiter immédiatement si demandé dans la configuration
        if current_app.config.get('NOTIFICATIONS_PROCESS_IMMEDIATELY', False):
            results = {}
            for notification in notifications:
                if notification.type == 'email':
                    results['email'] = self.email_service.process_notification(notification)
                elif notification.type == 'sms':
                    results['sms'] = self.sms_service.process_notification(notification)
                elif notification.type == 'push':
                    results['push'] = self.push_service.process_notification(notification)
            
            return {
                'success': True,
                'results': results,
                'notification_ids': [n.id for n in notifications]
            }
        
        # Sinon, retourner les IDs des notifications créées
        return {
            'success': True,
            'message': f"{len(notifications)} notifications mises en file d'attente",
            'notification_ids': [n.id for n in notifications]
        }
    
    def send_reminder(self, appointment_id, custom_message=None, days_before=1):
        """
        Envoyer un rappel pour un rendez-vous
        
        Args:
            appointment_id: ID du rendez-vous
            custom_message: Message personnalisé (optionnel)
            days_before: Jours avant le rendez-vous (défaut: 1)
            
        Returns:
            dict: Résultat de l'envoi
        """
        from app.models.appointment import Appointment
        
        # Récupérer le rendez-vous
        appointment = Appointment.query.get(appointment_id)
        if not appointment:
            return {'success': False, 'error': f"Rendez-vous {appointment_id} non trouvé"}
        
        # Récupérer le patient
        patient = Patient.query.get(appointment.patient_id)
        if not patient:
            return {'success': False, 'error': f"Patient {appointment.patient_id} non trouvé"}
        
        # Générer le message
        if not custom_message:
            if appointment.is_bilan:
                message = f"Rappel: Vous avez un bilan de kinésithérapie prévu le {appointment.date.strftime('%d/%m/%Y')} à {appointment.time.strftime('%H:%M')}. Pensez à apporter votre ordonnance médicale."
            else:
                message = f"Rappel: Vous avez une séance de kinésithérapie prévue le {appointment.date.strftime('%d/%m/%Y')} à {appointment.time.strftime('%H:%M')}."
        else:
            message = custom_message
        
        # Sujet pour l'email
        subject = f"Rappel de rendez-vous - {appointment.date.strftime('%d/%m/%Y')}"
        
        # Envoyer la notification
        return self.notify_patient(
            patient_id=patient.id,
            message=message,
            subject=subject,
            appointment_id=appointment_id
        )
    
    def send_bilan_alert(self, patient_id, days_overdue=None):
        """
        Envoyer une alerte de bilan requis
        
        Args:
            patient_id: ID du patient
            days_overdue: Nombre de jours de dépassement (optionnel)
            
        Returns:
            dict: Résultat de l'envoi
        """
        # Récupérer le patient
        patient = Patient.query.get(patient_id)
        if not patient:
            return {'success': False, 'error': f"Patient {patient_id} non trouvé"}
        
        # Générer le message
        message = f"Bonjour {patient.first_name},\n\nNous vous informons qu'un bilan de kinésithérapie est nécessaire "
        
        if days_overdue:
            message += f"(le dernier date de plus de {days_overdue} jours). "
        else:
            message += "pour la poursuite de vos soins. "
        
        message += "Merci de contacter le cabinet pour programmer un rendez-vous de bilan.\n\nCordialement,\nVotre kinésithérapeute."
        
        # Sujet pour l'email
        subject = "Bilan de kinésithérapie requis"
        
        # Envoyer la notification
        return self.notify_patient(
            patient_id=patient.id,
            message=message,
            subject=subject
        )
    
    def process_all_pending(self):
        """
        Traiter toutes les notifications en attente
        
        Returns:
            dict: Résultats du traitement par type
        """
        from app.services.notification.email import process_email_notifications
        from app.services.notification.sms import process_sms_notifications
        from app.services.notification.push import process_push_notifications
        
        results = {
            'email': process_email_notifications(),
            'sms': process_sms_notifications(),
            'push': process_push_notifications()
        }
        
        total_processed = sum(results.values())
        logger.info(f"Traitement terminé: {total_processed} notifications traitées")
        
        return {
            'success': True,
            'total_processed': total_processed,
            'results': results
        }