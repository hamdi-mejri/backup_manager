# Utilise une image de base Python officielle
FROM python:3.12-slim

# Définir le répertoire de travail dans le conteneur
WORKDIR /app

# Copier tout le contenu de ton projet dans le conteneur
COPY . .

# Installer les dépendances si tu en as (ajuste si besoin)
#RUN pip install -r requirements.txt

# Créer les dossiers s’ils n'existent pas
RUN mkdir -p logs backups

# Spécifie la commande de lancement par défaut (modifiable avec docker run)
CMD ["python", "backup_manager.py", "start"]