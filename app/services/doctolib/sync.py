"""
Service de synchronisation des rendez-vous avec Doctolib
"""

import asyncio
import logging
from datetime import datetime, timedelta
import re
from flask import current_app
from app import db
from app.models.patient import Patient
from app.models.appointment import Appointment
from app.models.notification import Notification
from app.services.doctolib.scraper import DoctolibScraper
from app.services.notification.manager import NotificationManager

logger = logging.getLogger(__name__)

class DoctolibSyncService:
    """Service de synchronisation des rendez-vous avec Doctolib"""
    
    def __init__(self):
        """Initialisation du service"""
        self.email = current_app.config.get('DOCTOLIB_EMAIL')
        self.password = current_app.config.get('DOCTOLIB_PASSWORD')
        self.url = current_app.config.get('DOCTOLIB_URL')
        self.auto_cancel = current_app.config.get('AUTO_CANCEL_ENABLED', False)
        self.max_days = current_app.config.get('BILAN_MAX_DAYS', 60)
    
    async def sync_appointments(self, days=30):
        """
        Synchroniser les rendez-vous depuis Doctolib
        
        Args:
            days: Nombre de jours à synchroniser (défaut: 30)
            
        Returns:
            dict: Résultats de la synchronisation
        """
        if not self.email or not self.password:
            logger.error("Configuration Doctolib incomplète")
            return {
                'success': False,
                'error': "Configuration Doctolib incomplète"
            }
        
        # Stats
        results = {
            'total_appointments': 0,
            'new_appointments': 0,
            'updated_appointments': 0,
            'new_patients': 0,
            'cancelled_appointments': 0,
            'errors': []
        }
        
        try:
            async with DoctolibScraper(self.email, self.password, self.url) as scraper:
                # Se connecter à Doctolib
                login_success = await scraper.login()
                if not login_success:
                    logger.error("Échec de connexion à Doctolib")
                    return {
                        'success': False,
                        'error': "Échec de connexion à Doctolib"
                    }
                
                # Définir la période à synchroniser
                start_date = datetime.now().date()
                end_date = start_date + timedelta(days=days)
                
                # Récupérer les rendez-vous
                appointments = await scraper.get_appointments(start_date, end_date)
                results['total_appointments'] = len(appointments)
                
                # Traiter chaque rendez-vous
                for appointment_data in appointments:
                    try:
                        # Extraire les informations du rendez-vous
                        doctolib_id = appointment_data.get('id')
                        patient_name = appointment_data.get('patientName', '')
                        date_str = appointment_data.get('date', '')
                        time_str = appointment_data.get('time', '')
                        motif = appointment_data.get('motif', '')
                        
                        # Vérifier si les données sont valides
                        if not (doctolib_id and patient_name and date_str and time_str):
                            results['errors'].append(f"Données de rendez-vous incomplètes: {appointment_data}")
                            continue
                        
                        # Parser les informations du patient
                        patient_info = self._parse_patient_name(patient_name)
                        
                        # Rechercher ou créer le patient
                        patient = self._find_or_create_patient(patient_info)
                        if patient.id is None:  # Nouveau patient
                            db.session.add(patient)
                            db.session.flush()  # Obtenir l'ID généré
                            results['new_patients'] += 1
                        
                        # Parser la date et l'heure
                        try:
                            appointment_date = datetime.strptime(date_str, "%d/%m/%Y").date()
                            appointment_time = datetime.strptime(time_str, "%H:%M").time()
                        except ValueError:
                            results['errors'].append(f"Erreur de format de date/heure: {date_str} {time_str}")
                            continue
                        
                        # Vérifier si c'est un bilan
                        is_bilan = self._is_bilan_appointment(motif)
                        
                        # Vérifier si le rendez-vous existe déjà
                        existing_appointment = Appointment.query.filter_by(doctolib_id=doctolib_id).first()
                        
                        if existing_appointment:
                            # Mise à jour du rendez-vous existant
                            existing_appointment.date = appointment_date
                            existing_appointment.time = appointment_time
                            existing_appointment.is_bilan = is_bilan
                            existing_appointment.type = 'bilan' if is_bilan else 'regular'
                            existing_appointment.notes = motif
                            results['updated_appointments'] += 1
                        else:
                            # Création d'un nouveau rendez-vous
                            new_appointment = Appointment(
                                patient_id=patient.id,
                                date=appointment_date,
                                time=appointment_time,
                                doctolib_id=doctolib_id,
                                is_bilan=is_bilan,
                                type='bilan' if is_bilan else 'regular',
                                notes=motif
                            )
                            db.session.add(new_appointment)
                            results['new_appointments'] += 1
                            
                            # Si c'est un bilan, mettre à jour la date du dernier bilan du patient
                            if is_bilan:
                                patient.last_bilan_date = appointment_date
                        
                        # Vérification de la conformité au bilan (si activé)
                        if self.auto_cancel and not is_bilan:
                            needs_bilan = patient.needs_bilan(self.max_days)
                            if needs_bilan:
                                # Le patient a besoin d'un bilan mais ce n'est pas un rendez-vous de bilan
                                if existing_appointment and existing_appointment.status == 'scheduled':
                                    # Annuler le rendez-vous dans Doctolib
                                    cancel_success = await scraper.cancel_appointment(
                                        doctolib_id,
                                        "Besoin d'un bilan obligatoire avant de poursuivre les soins"
                                    )
                                    
                                    if cancel_success:
                                        existing_appointment.status = 'cancelled'
                                        results['cancelled_appointments'] += 1
                                        
                                        # Créer une notification pour informer le patient
                                        notification_manager = NotificationManager()
                                        notification_manager.send_bilan_alert(
                                            patient_id=patient.id,
                                            days_overdue=(datetime.now().date() - patient.last_bilan_date).days if patient.last_bilan_date else None
                                        )
                    
                    except Exception as e:
                        results['errors'].append(f"Erreur lors du traitement du rendez-vous: {str(e)}")
                
                # Enregistrer les modifications
                db.session.commit()
                
                # Résumé de la synchronisation
                logger.info(f"Synchronisation terminée: {results['new_appointments']} nouveaux rendez-vous, "
                            f"{results['updated_appointments']} rendez-vous mis à jour, "
                            f"{results['new_patients']} nouveaux patients, "
                            f"{results['cancelled_appointments']} rendez-vous annulés")
                
                return {
                    'success': True,
                    'results': results
                }
        
        except Exception as e:
            logger.error(f"Erreur de synchronisation Doctolib: {str(e)}")
            return {
                'success': False,
                'error': f"Erreur de synchronisation: {str(e)}"
            }
    
    def _parse_patient_name(self, patient_name):
        """
        Parser le nom du patient depuis le format Doctolib
        
        Args:
            patient_name: Nom complet du patient (format: "NOM Prénom")
            
        Returns:
            dict: Informations du patient (first_name, last_name)
        """
        parts = patient_name.strip().split(' ')
        if len(parts) >= 2:
            # Si le nom est en majuscules, on le considère comme le nom de famille
            if parts[0].isupper():
                last_name = parts[0]
                first_name = ' '.join(parts[1:])
            else:
                # Sinon, on prend le dernier élément comme nom de famille
                last_name = parts[-1]
                first_name = ' '.join(parts[:-1])
        else:
            # Si un seul mot, on le considère comme le nom de famille
            last_name = patient_name
            first_name = ""
        
        return {
            'first_name': first_name.strip(),
            'last_name': last_name.strip()
        }
    
    def _find_or_create_patient(self, patient_info):
        """
        Rechercher un patient ou en créer un nouveau
        
        Args:
            patient_info: Dictionnaire avec first_name et last_name
            
        Returns:
            Patient: Instance du patient trouvé ou créé
        """
        # Rechercher par nom et prénom
        patient = Patient.query.filter_by(
            first_name=patient_info['first_name'],
            last_name=patient_info['last_name']
        ).first()
        
        if not patient:
            # Créer un nouveau patient
            patient = Patient(
                first_name=patient_info['first_name'],
                last_name=patient_info['last_name']
            )
        
        return patient
    
    def _is_bilan_appointment(self, motif):
        """
        Déterminer si un rendez-vous est un bilan basé sur le motif
        
        Args:
            motif: Motif du rendez-vous
            
        Returns:
            bool: True si c'est un bilan, False sinon
        """
        if not motif:
            return False
        
        # Mots-clés qui indiquent un bilan
        bilan_keywords = ['bilan', 'diagnostic', 'première séance', 'première consultation', 'initial']
        
        # Vérifier si l'un des mots-clés est présent
        motif_lower = motif.lower()
        return any(keyword in motif_lower for keyword in bilan_keywords)

def sync_doctolib():
    """
    Fonction pour synchroniser les rendez-vous avec Doctolib (à exécuter périodiquement)
    """
    with current_app.app_context():
        service = DoctolibSyncService()
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(service.sync_appointments())
        loop.close()
        return result