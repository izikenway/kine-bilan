"""
Configuration par défaut de l'application
"""

import os
from datetime import timedelta

# Configuration de base
SECRET_KEY = os.environ.get('SECRET_KEY', 'cle_secrete_par_defaut')
SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URI', 'sqlite:///app.db')
SQLALCHEMY_TRACK_MODIFICATIONS = False

# Configuration JWT
JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY', SECRET_KEY)
JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)
JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)

# Configuration Doctolib
DOCTOLIB_EMAIL = os.environ.get('DOCTOLIB_EMAIL')
DOCTOLIB_PASSWORD = os.environ.get('DOCTOLIB_PASSWORD')
DOCTOLIB_URL = os.environ.get('DOCTOLIB_URL', 'https://www.doctolib.fr/')

# Configuration des emails
SMTP_SERVER = os.environ.get('SMTP_SERVER')
SMTP_PORT = int(os.environ.get('SMTP_PORT', 587))
SMTP_USERNAME = os.environ.get('SMTP_USERNAME')
SMTP_PASSWORD = os.environ.get('SMTP_PASSWORD')
EMAIL_SENDER = os.environ.get('EMAIL_SENDER')

# Configuration SMS (Twilio)
TWILIO_ACCOUNT_SID = os.environ.get('TWILIO_ACCOUNT_SID')
TWILIO_AUTH_TOKEN = os.environ.get('TWILIO_AUTH_TOKEN')
TWILIO_PHONE_NUMBER = os.environ.get('TWILIO_PHONE_NUMBER')

# Configuration Firebase
FIREBASE_CREDENTIALS_PATH = os.environ.get('FIREBASE_CREDENTIALS_PATH')

# Configuration métier
BILAN_MAX_DAYS = int(os.environ.get('BILAN_MAX_DAYS', 60))
AUTO_CANCEL_ENABLED = os.environ.get('AUTO_CANCEL_ENABLED', 'true').lower() in ('true', '1', 't')
SYNC_INTERVAL_MINUTES = int(os.environ.get('SYNC_INTERVAL_MINUTES', 60))