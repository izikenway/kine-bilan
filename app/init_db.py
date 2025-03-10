#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Script d'initialisation de la base de données
"""

import os
import sys
from dotenv import load_dotenv

# Ajouter le répertoire parent au PYTHONPATH
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Charger les variables d'environnement
load_dotenv()

from app import create_app, db
from app.models.user import User

def init_db():
    """Initialiser la base de données avec des données de base"""
    app = create_app()
    
    with app.app_context():
        # Créer toutes les tables
        db.create_all()
        
        # Vérifier si un utilisateur admin existe déjà
        admin = User.query.filter_by(email='admin@exemple.com').first()
        
        if not admin:
            # Créer un utilisateur admin par défaut
            admin = User(
                email='admin@exemple.com',
                password='admin123',  # À changer en production !
                name='Administrateur',
                role='admin'
            )
            db.session.add(admin)
            db.session.commit()
            print("Utilisateur admin créé avec succès.")
        else:
            print("Un utilisateur admin existe déjà.")
        
        print("Base de données initialisée avec succès.")

if __name__ == "__main__":
    init_db()