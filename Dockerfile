FROM python:3.11-slim

# Définir le répertoire de travail
WORKDIR /app

# Installer les dépendances systèmes pour Playwright et les autres outils
RUN apt-get update && apt-get install -y \
    wget \
    curl \
    gnupg \
    libglib2.0-0 \
    libnss3 \
    libnspr4 \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libcups2 \
    libdrm2 \
    libdbus-1-3 \
    libexpat1 \
    libxcb1 \
    libxkbcommon0 \
    libx11-6 \
    libxcomposite1 \
    libxdamage1 \
    libxext6 \
    libxfixes3 \
    libxrandr2 \
    libgbm1 \
    libpango-1.0-0 \
    libcairo2 \
    libasound2 \
    && rm -rf /var/lib/apt/lists/*

# Copier les fichiers requirements.txt
COPY requirements.txt .

# Installer les dépendances Python
RUN pip install --no-cache-dir -r requirements.txt

# Installer Playwright
RUN python -m playwright install chromium --with-deps

# Copier tout le code source
COPY . .

# Variable d'environnement pour indiquer que nous sommes en production
ENV FLASK_ENV=production
ENV PYTHONUNBUFFERED=1

# Exposer le port sur lequel l'application s'exécute
EXPOSE 5000

# Commande pour démarrer l'application avec Gunicorn
CMD ["gunicorn", "--worker-class", "gevent", "--workers", "4", "--bind", "0.0.0.0:5000", "run:app"] 