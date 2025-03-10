"""
Service d'envoi de notifications par email
"""

import smtplib
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from app import db
from app.models.notification import Notification
from flask import current_app

logger = logging.getLogger(__name__)

class EmailService:
    """Service d'envoi d'emails"""
    
    def __init__(self):
        """Initialisation avec les paramètres de configuration"""
        self.smtp_server = current_app.config.get('SMTP_SERVER')
        self.smtp_port = current_app.config.get('SMTP_PORT')
        self.smtp_username = current_app.config.get('SMTP_USERNAME')
        self.smtp_password = current_app.config.get('SMTP_PASSWORD')
        self.email_sender = current_app.config.get('EMAIL_SENDER')
    
    def send_email(self, recipient, subject, message, html_content=None):
        """Envoyer un email à un destinataire"""
        if not self.smtp_server or not self.smtp_username or not self.smtp_password:
            logger.error("Configuration SMTP incomplète")
            return False, "Configuration SMTP incomplète"
        
        try:
            # Créer le message
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = self.email_sender
            msg['To'] = recipient
            
            # Ajouter le contenu texte
            text_part = MIMEText(message, 'plain')
            msg.attach(text_part)
            
            # Ajouter le contenu HTML si fourni
            if html_content:
                html_part = MIMEText(html_content, 'html')
                msg.attach(html_part)
            
            # Établir la connexion et envoyer
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_username, self.smtp_password)
                server.send_message(msg)
            
            logger.info(f"Email envoyé à {recipient}")
            return True, None
        
        except Exception as e:
            error_msg = f"Erreur lors de l'envoi de l'email: {str(e)}"
            logger.error(error_msg)
            return False, error_msg
    
    def process_notification(self, notification):
        """Traiter une notification par email"""
        from app.models.patient import Patient
        
        # Récupérer le patient
        patient = Patient.query.get(notification.patient_id)
        if not patient or not patient.email:
            notification.mark_as_failed("Patient sans email valide")
            return False
        
        # Envoyer l'email
        success, error = self.send_email(
            recipient=patient.email,
            subject=notification.subject or "Notification de KinéBilan",
            message=notification.message
        )
        
        # Mettre à jour le statut de la notification
        if success:
            notification.mark_as_sent()
        else:
            notification.mark_as_failed(error)
        
        return success

def process_email_notifications():
    """Fonction pour traiter toutes les notifications email en attente"""
    with current_app.app_context():
        # Récupérer les notifications email en attente
        notifications = Notification.query.filter_by(
            type='email',
            status='pending'
        ).all()
        
        if not notifications:
            logger.info("Aucune notification email en attente")
            return 0
        
        # Initialiser le service d'email
        email_service = EmailService()
        
        # Traiter chaque notification
        success_count = 0
        for notification in notifications:
            if email_service.process_notification(notification):
                success_count += 1
        
        logger.info(f"Traitement terminé: {success_count}/{len(notifications)} emails envoyés avec succès")
        return success_count