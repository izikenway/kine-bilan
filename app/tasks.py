#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Tâches périodiques pour l'application KinéBilan.
Ce script peut être exécuté par un planificateur comme cron.
"""

import os
import sys
import logging
import argparse
from datetime import datetime
from dotenv import load_dotenv

# Ajouter le répertoire parent au PYTHONPATH
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Charger les variables d'environnement
load_dotenv()

from app import create_app
from app.services.doctolib.sync import sync_doctolib
from app.services.notification.manager import NotificationManager
from app.models.appointment import Appointment
from app.models.patient import Patient
from datetime import datetime, timedelta

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('tasks.log')
    ]
)

logger = logging.getLogger(__name__)

def sync_appointments():
    """Synchroniser les rendez-vous avec Doctolib"""
    logger.info("Démarrage de la synchronisation des rendez-vous")
    result = sync_doctolib()
    
    if result['success']:
        logger.info(f"Synchronisation terminée avec succès: {result['results']}")
    else:
        logger.error(f"Échec de la synchronisation: {result.get('error', 'Erreur inconnue')}")
    
    return result

def process_notifications():
    """Traiter les notifications en attente"""
    logger.info("Démarrage du traitement des notifications")
    
    notification_manager = NotificationManager()
    result = notification_manager.process_all_pending()
    
    logger.info(f"Traitement terminé: {result['total_processed']} notifications traitées")
    
    return result

def send_appointment_reminders(days_before=1):
    """Envoyer des rappels pour les rendez-vous à venir"""
    logger.info(f"Envoi des rappels pour les rendez-vous dans {days_before} jours")
    
    # Date cible
    target_date = datetime.now().date() + timedelta(days=days_before)
    
    # Récupérer les rendez-vous pour la date cible
    with create_app().app_context():
        appointments = Appointment.query.filter(
            Appointment.date == target_date,
            Appointment.status == 'scheduled'
        ).all()
        
        logger.info(f"Envoi de rappels pour {len(appointments)} rendez-vous")
        
        notification_manager = NotificationManager()
        success_count = 0
        
        for appointment in appointments:
            result = notification_manager.send_reminder(
                appointment_id=appointment.id,
                days_before=days_before
            )
            
            if result['success']:
                success_count += 1
        
        logger.info(f"Envoi de rappels terminé: {success_count}/{len(appointments)} envoyés avec succès")
        
        return {
            'success': True,
            'total': len(appointments),
            'success_count': success_count
        }

def check_bilans():
    """Vérifier les patients qui ont besoin d'un bilan"""
    logger.info("Vérification des patients qui ont besoin d'un bilan")
    
    with create_app().app_context():
        today = datetime.now().date()
        max_days = int(os.environ.get('BILAN_MAX_DAYS', 60))
        
        # Récupérer les patients qui ont besoin d'un bilan
        patients = Patient.query.filter(
            (Patient.last_bilan_date == None) | 
            ((today - Patient.last_bilan_date) >= max_days)
        ).all()
        
        logger.info(f"{len(patients)} patients ont besoin d'un bilan")
        
        notification_manager = NotificationManager()
        success_count = 0
        
        for patient in patients:
            days_overdue = None
            if patient.last_bilan_date:
                days_overdue = (today - patient.last_bilan_date).days
            
            result = notification_manager.send_bilan_alert(
                patient_id=patient.id,
                days_overdue=days_overdue
            )
            
            if result['success']:
                success_count += 1
        
        logger.info(f"Envoi d'alertes de bilan terminé: {success_count}/{len(patients)} envoyées avec succès")
        
        return {
            'success': True,
            'total': len(patients),
            'success_count': success_count
        }

def main():
    """Fonction principale pour exécuter les tâches"""
    parser = argparse.ArgumentParser(description="Exécuter des tâches périodiques pour KinéBilan")
    parser.add_argument('task', choices=['sync', 'notifications', 'reminders', 'bilans', 'all'],
                        help="Tâche à exécuter")
    parser.add_argument('--days', type=int, default=1,
                        help="Nombre de jours avant le rendez-vous pour les rappels (par défaut: 1)")
    
    args = parser.parse_args()
    
    app = create_app()
    with app.app_context():
        if args.task == 'sync' or args.task == 'all':
            sync_appointments()
        
        if args.task == 'notifications' or args.task == 'all':
            process_notifications()
        
        if args.task == 'reminders' or args.task == 'all':
            send_appointment_reminders(args.days)
        
        if args.task == 'bilans' or args.task == 'all':
            check_bilans()

if __name__ == "__main__":
    main()