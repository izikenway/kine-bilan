"""
Service d'envoi de notifications push via Firebase Cloud Messaging
"""

import logging
import firebase_admin
from firebase_admin import credentials, messaging
from app import db
from app.models.notification import Notification
from flask import current_app

logger = logging.getLogger(__name__)

class PushService:
    """Service d'envoi de notifications push via Firebase"""
    
    _instance = None
    _initialized = False
    
    def __new__(cls):
        """Singleton pattern pour éviter les initialisations multiples"""
        if cls._instance is None:
            cls._instance = super(PushService, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        """Initialisation avec les paramètres de configuration"""
        if PushService._initialized:
            return
        
        self.credentials_path = current_app.config.get('FIREBASE_CREDENTIALS_PATH')
        self.initialized = False
        
        # Initialiser Firebase si les credentials sont disponibles
        if self.credentials_path:
            try:
                cred = credentials.Certificate(self.credentials_path)
                firebase_admin.initialize_app(cred)
                self.initialized = True
                logger.info("Firebase initialisé avec succès")
            except Exception as e:
                logger.error(f"Erreur lors de l'initialisation de Firebase: {str(e)}")
        
        PushService._initialized = True
    
    def send_push(self, token, title, body, data=None):
        """Envoyer une notification push à un token d'appareil"""
        if not self.initialized:
            logger.error("Firebase non initialisé")
            return False, "Firebase non initialisé"
        
        try:
            # Préparer le message
            message = messaging.Message(
                notification=messaging.Notification(
                    title=title,
                    body=body
                ),
                data=data or {},
                token=token
            )
            
            # Envoyer la notification
            response = messaging.send(message)
            logger.info(f"Notification push envoyée, message_id: {response}")
            return True, response
        
        except Exception as e:
            error_msg = f"Erreur lors de l'envoi de la notification push: {str(e)}"
            logger.error(error_msg)
            return False, error_msg
    
    def send_to_topic(self, topic, title, body, data=None):
        """Envoyer une notification push à un topic"""
        if not self.initialized:
            logger.error("Firebase non initialisé")
            return False, "Firebase non initialisé"
        
        try:
            # Préparer le message
            message = messaging.Message(
                notification=messaging.Notification(
                    title=title,
                    body=body
                ),
                data=data or {},
                topic=topic
            )
            
            # Envoyer la notification
            response = messaging.send(message)
            logger.info(f"Notification push envoyée au topic {topic}, message_id: {response}")
            return True, response
        
        except Exception as e:
            error_msg = f"Erreur lors de l'envoi de la notification push au topic: {str(e)}"
            logger.error(error_msg)
            return False, error_msg
    
    def process_notification(self, notification):
        """Traiter une notification push"""
        from app.models.patient import Patient
        from app.models.user_device import UserDevice
        
        # Récupérer le patient
        patient = Patient.query.get(notification.patient_id)
        if not patient:
            notification.mark_as_failed("Patient non trouvé")
            return False
        
        # Récupérer les tokens d'appareils associés au patient
        devices = UserDevice.query.filter_by(patient_id=patient.id, active=True).all()
        if not devices:
            notification.mark_as_failed("Aucun appareil enregistré pour ce patient")
            return False
        
        # Préparer le titre et le corps du message
        title = notification.subject or "Notification KinéBilan"
        body = notification.message[:100]  # Limiter la longueur du corps
        
        # Variables pour suivre les succès/échecs
        success_count = 0
        errors = []
        
        # Envoyer à chaque appareil
        for device in devices:
            success, result = self.send_push(
                token=device.token,
                title=title,
                body=body,
                data={
                    'notification_id': str(notification.id),
                    'patient_id': str(patient.id),
                    'full_message': notification.message
                }
            )
            
            if success:
                success_count += 1
            else:
                errors.append(result)
        
        # Mettre à jour le statut de la notification
        if success_count > 0:
            notification.mark_as_sent()
            return True
        else:
            notification.mark_as_failed("\n".join(errors))
            return False

def process_push_notifications():
    """Fonction pour traiter toutes les notifications push en attente"""
    with current_app.app_context():
        # Récupérer les notifications push en attente
        notifications = Notification.query.filter_by(
            type='push',
            status='pending'
        ).all()
        
        if not notifications:
            logger.info("Aucune notification push en attente")
            return 0
        
        # Initialiser le service push
        push_service = PushService()
        
        # Traiter chaque notification
        success_count = 0
        for notification in notifications:
            if push_service.process_notification(notification):
                success_count += 1
        
        logger.info(f"Traitement terminé: {success_count}/{len(notifications)} notifications push envoyées avec succès")
        return success_count