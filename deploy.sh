#!/bin/bash

# Script de déploiement pour l'application KinéBilan
# Ce script met à jour et démarre l'application en utilisant Docker Compose

# Arrêter l'exécution en cas d'erreur
set -e

echo "🚀 Démarrage du déploiement de KinéBilan..."

# Vérifier que Docker est installé
if ! command -v docker &> /dev/null; then
    echo "❌ Docker n'est pas installé. Veuillez installer Docker et réessayer."
    exit 1
fi

# Vérifier que Docker Compose est installé
if ! docker compose version &> /dev/null; then
    echo "❌ Docker Compose n'est pas installé. Veuillez installer Docker Compose et réessayer."
    exit 1
fi

# Créer les répertoires nécessaires s'ils n'existent pas
mkdir -p logs
mkdir -p data

# Mettre à jour le code depuis le dépôt Git (si applicable)
# git pull origin main

# Construire les images Docker
echo "🔨 Construction des images Docker..."
docker compose build

# Démarrer les services
echo "🌐 Démarrage des services..."
docker compose up -d

# Vérifier que les services sont bien démarrés
echo "✅ Vérification des services..."
docker compose ps

echo "🎉 Déploiement terminé ! L'application est accessible sur http://localhost:5000" 