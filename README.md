# KinéBilan - Gestion Automatisée des Bilans pour Kinésithérapeutes

Application permettant aux kinésithérapeutes de gérer automatiquement les bilans obligatoires pour leurs patients, en s'intégrant avec Doctolib.

## Fonctionnalités Principales

- **Automatisation Web** : Extraction optimisée des données depuis Doctolib via Playwright avec mise en cache des sessions
- **Vérification des Bilans** : Contrôle automatique de la conformité des rendez-vous (bilan tous les 2 mois)
- **Actions Automatisées** : Annulation des rendez-vous non conformes et envoi de notifications multi-canaux
- **Interface Web** : Tableau de bord réactif pour visualiser et gérer les rendez-vous et bilans
- **Application Mobile** : Accès aux fonctionnalités essentielles en déplacement avec mode hors ligne
- **Notifications** : Alertes par e-mail, SMS et notifications push avec personnalisation avancée
- **Rapports** : Statistiques et rapports détaillés sur les bilans et rendez-vous
- **Sécurité RGPD** : Chiffrement avancé des données, pseudonymisation et outils d'anonymisation conformes

## Améliorations de la Version 2.0

- **Sécurité renforcée** : Chiffrement avancé des données avec dérivation de clé (PBKDF2)
- **Conformité RGPD** : Pseudonymisation des identifiants, hashage pour les recherches et anonymisation simplifiée
- **Performance** : Mise en cache des sessions Doctolib et optimisation des extractions
- **Robustesse** : Utilisation de Redis Queue (RQ) pour les tâches asynchrones avec retries automatiques
- **Scalabilité** : Architecture modulaire prête pour le cloud et schéma de base optimisé
- **Mode Hors Ligne** : Support amélioré pour l'application mobile avec synchronisation différée

## Architecture Technique

- **Back-end** : Python 3.11+ avec Flask 2.3
- **Automatisation** : Playwright pour Python avec optimisations
- **Base de Données** : SQLite avec SQLAlchemy 2.0 (migration PostgreSQL possible)
- **File d'attente** : Redis Queue (RQ) pour les tâches asynchrones
- **Front-end Web** : React avec hooks
- **Application Mobile** : React Native avec support hors ligne
- **Notifications** : SMTP/Gmail API, Twilio, Firebase Cloud Messaging
- **Déploiement** : Docker, Gunicorn et supervisord

## Installation

1. Cloner le dépôt :
```bash
git clone https://github.com/votre-utilisateur/kine-bilan.git
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
python -m playwright install chromium
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

## Configuration Redis (nouveau)

Pour utiliser Redis Queue pour les tâches asynchrones :

1. Installer Redis :
```bash
# Ubuntu/Debian
sudo apt-get install redis-server

# macOS avec Homebrew
brew install redis
```

2. Démarrer Redis :
```bash
redis-server
```

3. Démarrer les workers RQ :
```bash
# Dans un terminal séparé
python -m rq worker sync verify export purge high
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

## Migration de la base de données vers v2.0

Pour migrer une base de données existante vers la nouvelle structure :

```bash
python -m app.migrations.migration_v1_a_v2
```

Cette commande :
- Créera une sauvegarde de votre base de données actuelle
- Ajoutera les nouvelles colonnes requises
- Mettra à jour les données existantes avec les nouveaux formats
- Générera les identifiants de pseudonymisation (UIDs)

## Configuration

Les paramètres de l'application peuvent être configurés via l'interface web ou directement dans la base de données :

- Délai maximal entre bilans (par défaut : 60 jours)
- Fréquence de synchronisation avec Doctolib
- Activation/désactivation de l'annulation automatique
- Canaux de notification (e-mail, SMS, push)
- Modèles de messages
- Mode "Économie de données" pour l'application mobile

## Sécurité

- Authentification avec JWT et tokens de rafraîchissement
- Chiffrement avancé des données sensibles avec PBKDF2
- Communication HTTPS obligatoire
- Protection contre les injections SQL et XSS
- Pseudonymisation des identifiants et anonymisation conforme RGPD

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
│   │   └── ...         # Autres sous-répertoires
│   ├── utils/          # Utilitaires
│   ├── config/         # Configuration
│   ├── migrations/     # Scripts de migration de base
│   ├── static/         # Fichiers statiques
│   ├── templates/      # Templates (si nécessaire)
│   └── tests/          # Tests unitaires et d'intégration
├── migrations/         # Migrations Alembic
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

Exécuter les tests avec couverture :
```bash
pytest --cov=app tests/
```

## Déploiement Docker

L'application peut être déployée facilement en utilisant Docker et Docker Compose :

```bash
# Rendre le script de déploiement exécutable
chmod +x deploy.sh

# Exécuter le script de déploiement
./deploy.sh
```

Ou manuellement :

```bash
# Créer les répertoires nécessaires
mkdir -p logs data

# Construire les images Docker
docker compose build

# Démarrer les services
docker compose up -d
```

L'application sera accessible à l'adresse suivante :
```
http://localhost:5000
```

### Logs et surveillance

Pour consulter les logs de l'application :
```bash
docker compose logs -f web
```

Pour consulter les logs des workers RQ :
```bash
docker compose logs -f rq-worker
```

### Mise à jour de l'application

Pour mettre à jour l'application :
```bash
git pull  # Si vous utilisez Git pour gérer votre code
./deploy.sh
```

### Sauvegarde des données

Les données sont stockées dans des volumes Docker :
- `redis_data` pour Redis
- `./data` pour les fichiers de l'application
- `./logs` pour les logs

Pour sauvegarder ces données, vous pouvez utiliser les commandes standard de Docker et de votre système d'exploitation.

## Licence

Ce projet est sous licence [MIT](LICENSE).

## Contact

Pour toute question ou suggestion, veuillez contacter [votre-email@exemple.com](mailto:votre-email@exemple.com). 