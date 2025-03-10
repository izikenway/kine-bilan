"""
KinéBilan - Application de gestion automatisée des bilans pour kinésithérapeutes
"""

import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_migrate import Migrate

# Initialisation des extensions
db = SQLAlchemy()
jwt = JWTManager()
migrate = Migrate()

def create_app(config=None):
    """Création et configuration de l'application Flask"""
    app = Flask(__name__)
    
    # Configuration
    app.config.from_object('app.config.default')
    if config:
        app.config.update(config)
    
    # Initialisation des extensions avec l'application
    db.init_app(app)
    jwt.init_app(app)
    migrate.init_app(app, db)
    
    # Importation et enregistrement des blueprints
    from app.api import api_bp
    app.register_blueprint(api_bp, url_prefix='/api')
    
    # Gestion des erreurs
    @app.errorhandler(404)
    def page_not_found(e):
        return {"message": "Page non trouvée"}, 404
    
    @app.errorhandler(500)
    def internal_server_error(e):
        return {"message": "Erreur interne du serveur"}, 500
    
    return app