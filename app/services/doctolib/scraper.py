"""
Module de scraping pour Doctolib utilisant Playwright
"""

import asyncio
import logging
from datetime import datetime, timedelta
from playwright.async_api import async_playwright

logger = logging.getLogger(__name__)

class DoctolibScraper:
    """Classe pour l'automatisation des interactions avec Doctolib"""
    
    def __init__(self, email, password, base_url="https://www.doctolib.fr/"):
        self.email = email
        self.password = password
        self.base_url = base_url
        self.browser = None
        self.context = None
        self.page = None
    
    async def __aenter__(self):
        """Initialisation du navigateur avec le context manager"""
        playwright = await async_playwright().start()
        self.browser = await playwright.chromium.launch(headless=True)
        self.context = await self.browser.new_context()
        self.page = await self.context.new_page()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Fermeture du navigateur avec le context manager"""
        if self.browser:
            await self.browser.close()
    
    async def login(self):
        """Se connecter à Doctolib"""
        try:
            await self.page.goto(f"{self.base_url}connexion")
            await self.page.fill('input[name="username"]', self.email)
            await self.page.click('button[type="submit"]')
            await self.page.fill('input[name="password"]', self.password)
            await self.page.click('button[type="submit"]')
            
            # Attendre que la page soit chargée
            await self.page.wait_for_selector('div.dashboard')
            logger.info("Connexion à Doctolib réussie")
            return True
        except Exception as e:
            logger.error(f"Erreur lors de la connexion à Doctolib: {e}")
            return False
    
    async def get_appointments(self, start_date=None, end_date=None):
        """Récupérer les rendez-vous dans la période spécifiée"""
        if not start_date:
            start_date = datetime.now().date()
        if not end_date:
            end_date = start_date + timedelta(days=30)
        
        try:
            # Naviguer vers la page des rendez-vous
            await self.page.goto(f"{self.base_url}agenda")
            
            # Attendre que la liste des rendez-vous soit chargée
            await self.page.wait_for_selector('div.appointment-list')
            
            # Extraire les informations des rendez-vous
            appointments = await self.page.evaluate('''() => {
                const appointments = [];
                const elements = document.querySelectorAll('div.appointment-item');
                
                elements.forEach(element => {
                    const dateStr = element.querySelector('.date')?.innerText;
                    const timeStr = element.querySelector('.time')?.innerText;
                    const patientName = element.querySelector('.patient-name')?.innerText;
                    const motif = element.querySelector('.motif')?.innerText;
                    const id = element.getAttribute('data-appointment-id');
                    
                    if (dateStr && timeStr && patientName) {
                        appointments.push({
                            id,
                            date: dateStr,
                            time: timeStr,
                            patientName,
                            motif
                        });
                    }
                });
                
                return appointments;
            }''')
            
            logger.info(f"Récupération de {len(appointments)} rendez-vous")
            return appointments
        except Exception as e:
            logger.error(f"Erreur lors de la récupération des rendez-vous: {e}")
            return []
    
    async def cancel_appointment(self, appointment_id, reason="Besoin d'un bilan obligatoire"):
        """Annuler un rendez-vous avec un motif"""
        try:
            # Naviguer vers la page du rendez-vous
            await self.page.goto(f"{self.base_url}appointments/{appointment_id}")
            
            # Cliquer sur le bouton d'annulation
            await self.page.click('button.cancel-appointment')
            
            # Remplir le motif d'annulation
            await self.page.fill('textarea[name="cancel_reason"]', reason)
            
            # Confirmer l'annulation
            await self.page.click('button.confirm-cancel')
            
            # Attendre que l'annulation soit confirmée
            await self.page.wait_for_selector('div.cancel-confirmation')
            
            logger.info(f"Rendez-vous {appointment_id} annulé avec succès")
            return True
        except Exception as e:
            logger.error(f"Erreur lors de l'annulation du rendez-vous {appointment_id}: {e}")
            return False