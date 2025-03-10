"""
Service d'envoi de notifications par SMS via Twilio
"""

import logging
from twilio.rest import Client
from twilio.base.exceptions import TwilioRestException
from app import db
from app.models.notification import Notification
from flask import current_app

logger = logging.getLogger(__name__)

class SMSService:
    """Service d'envoi de SMS via Twilio"""
    
    def __init__(self):
        """Initialisation avec les paramètres de configuration"""
        self.account_sid = current_app.config.get('TWILIO_ACCOUNT_SID')
        self.auth_token = current_app.config.get('TWILIO_AUTH_TOKEN')
        self.phone_number = current_app.config.get('TWILIO_PHONE_NUMBER')
    
    def send_sms(self, recipient_phone, message):
        """Envoyer un SMS à un numéro de téléphone"""
        if not self.account_sid or not self.auth_token or not self.phone_number:
            logger.error("Configuration Twilio incomplète")
            return False, "Configuration Twilio incomplète"
        
        try:
            # Initialiser le client Twilio
            client = Client(self.account_sid, self.auth_token)
            
            # Formater le numéro de téléphone si nécessaire
            # Assurez-vous que le numéro est au format international (ex: +33612345678)
            if not recipient_phone.startswith('+'):
                # Si le numéro commence par un 0, le remplacer par +33 (pour la France)
                if recipient_phone.startswith('0') and len(recipient_phone) == 10:
                    recipient_phone = '+33' + recipient_phone[1:]
                else:
                    # Ajouter simplement un + au début
                    recipient_phone = '+' + recipient_phone
            
            # Envoyer le SMS
            sms = client.messages.create(
                body=message,
                from_=self.phone_number,
                to=recipient_phone
            )
            
            logger.info(f"SMS envoyé à {recipient_phone}, SID: {sms.sid}")
            return True, sms.sid
        
        except TwilioRestException as e:
            error_msg = f"Erreur Twilio: {e.msg}"
            logger.error(error_msg)
            return False, error_msg
        
        except Exception as e:
            error_msg = f"Erreur lors de l'envoi du SMS: {str(e)}"
            logger.error(error_msg)
            return False, error_msg
    
    def process_notification(self, notification):
        """Traiter une notification par SMS"""
        from app.models.patient import Patient
        
        # Récupérer le patient
        patient = Patient.query.get(notification.patient_id)
        if not patient or not patient.phone:
            notification.mark_as_failed("Patient sans numéro de téléphone valide")
            return False
        
        # Envoyer le SMS
        success, result = self.send_sms(
            recipient_phone=patient.phone,
            message=notification.message
        )
        
        # Mettre à jour le statut de la notification
        if success:
            notification.mark_as_sent()
        else:
            notification.mark_as_failed(result)
        
        return success

def process_sms_notifications():
    """Fonction pour traiter toutes les notifications SMS en attente"""
    with current_app.app_context():
        # Récupérer les notifications SMS en attente
        notifications = Notification.query.filter_by(
            type='sms',
            status='pending'
        ).all()
        
        if not notifications:
            logger.info("Aucune notification SMS en attente")
            return 0
        
        # Initialiser le service SMS
        sms_service = SMSService()
        
        # Traiter chaque notification
        success_count = 0
        for notification in notifications:
            if sms_service.process_notification(notification):
                success_count += 1
        
        logger.info(f"Traitement terminé: {success_count}/{len(notifications)} SMS envoyés avec succès")
        return success_count