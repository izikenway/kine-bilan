"""
API REST de l'application KinéBilan
"""

from flask import Blueprint

api_bp = Blueprint('api', __name__)

# Importation des routes
from app.api import auth, patients, appointments, reports

# Définition de la route principale de l'API
@api_bp.route('/')
def index():
    """Endpoint principal de l'API"""
    return {
        "name": "KinéBilan API",
        "version": "1.0.0",
        "status": "online"
    }