# KinéBilan - Gestion Automatisée des Bilans pour Kinésithérapeutes

Application permettant aux kinésithérapeutes de gérer automatiquement les bilans obligatoires pour leurs patients, en s'intégrant avec Doctolib.

## Fonctionnalités Principales

- **Automatisation Web** : Extraction des données depuis Doctolib via Playwright
- **Vérification des Bilans** : Contrôle automatique de la conformité des rendez-vous (bilan tous les 2 mois)
- **Actions Automatisées** : Annulation des rendez-vous non conformes et envoi de notifications
- **Interface Web** : Tableau de bord pour visualiser et gérer les rendez-vous et bilans
- **Application Mobile** : Accès aux fonctionnalités essentielles en déplacement
- **Notifications** : Alertes par e-mail, SMS et notifications push
- **Rapports** : Statistiques et rapports sur les bilans et rendez-vous

## Architecture Technique

- **Back-end** : Python avec Flask
- **Automatisation** : Playwright pour Python
- **Base de Données** : SQLite avec SQLAlchemy
- **Front-end Web** : React
- **Application Mobile** : React Native
- **Notifications** : SMTP, Twilio, Firebase Cloud Messaging

## Installation

1. Cloner le dépôt :
```bash
git clone https://github.com/izikenway/kine-bilan.git
cd kine-bilan
```

2. Créer un environnement virtuel et l'activer :
```bash
python -m venv venv
source venv/bin/activate  # Sur Windows : venv\Scripts\activate
```

3. Installer les dépendances :
```bash
pip install -r requirements.txt
```

4. Installer les navigateurs pour Playwright :
```bash
python -m playwright install
```

5. Configurer les variables d'environnement :
```bash
cp .env.example .env
# Éditer le fichier .env avec vos informations
```

6. Initialiser la base de données :
```bash
python app/init_db.py
```

## Démarrage

1. Lancer le serveur de développement :
```bash
python run.py
```

2. Accéder à l'interface web :
```
http://localhost:5000
```

## Configuration

Les paramètres de l'application peuvent être configurés via l'interface web ou directement dans la base de données :

- Délai maximal entre bilans (par défaut : 60 jours)
- Fréquence de synchronisation avec Doctolib
- Activation/désactivation de l'annulation automatique
- Canaux de notification (e-mail, SMS, push)
- Modèles de messages

## Sécurité

- Authentification avec JWT
- Chiffrement des données sensibles
- Communication HTTPS
- Conformité RGPD

## Développement

### Structure du Projet

```
kine-bilan/
├── app/
│   ├── api/            # Endpoints API REST
│   ├── models/         # Modèles SQLAlchemy
│   ├── services/       # Services métier
│   │   ├── doctolib/   # Automatisation Doctolib
│   │   ├── notification/ # Gestion des notifications
│   ├── utils/          # Utilitaires
│   ├── config/         # Configuration
│   ├── static/         # Fichiers statiques
│   ├── templates/      # Templates (si nécessaire)
│   └── tests/          # Tests unitaires et d'intégration
├── migrations/         # Migrations de base de données
├── .env                # Variables d'environnement
├── .env.example        # Exemple de variables d'environnement
├── requirements.txt    # Dépendances Python
└── run.py              # Point d'entrée de l'application
```

### Tests

Exécuter les tests unitaires :
```bash
pytest
```

Exécuter les tests d'intégration :
```bash
pytest tests/integration
```

## Licence

Ce projet est sous licence [MIT](LICENSE).

## Contact

Pour toute question ou suggestion, veuillez nous contacter.