# Système de Sauvegarde Automatisé

Un système de sauvegarde automatisé en Python qui permet de planifier et d'exécuter des sauvegardes de fichiers/dossiers à des heures spécifiques.

## 📋 Table des matières

- [Architecture](#architecture)
- [Fonctionnalités](#fonctionnalités)
- [Installation locale](#installation-locale)
- [Utilisation](#utilisation)
- [Déploiement Docker](#déploiement-docker)
- [Structure du projet](#structure-du-projet)
- [Exemples](#exemples)

## 🏗️ Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│                 │    │                  │    │                 │
│ backup_manager  │───▶│ backup_schedules │◀───│ backup_service  │
│     .py         │    │      .txt        │    │     .py         │
│                 │    │                  │    │                 │
│ • start/stop    │    │ format:          │    │ • boucle infinie│
│ • create/delete │    │ path;hh:mm;name  │    │ • vérif horaires│
│ • list          │    │                  │    │ • création .tar │
│ • backups       │    │                  │    │                 │
└─────────────────┘    └──────────────────┘    └─────────────────┘
         │                                               │
         │                                               │
         ▼                                               ▼
┌─────────────────┐                              ┌─────────────────┐
│                 │                              │                 │
│    ./logs/      │                              │   ./backups/    │
│                 │                              │                 │
│ backup_manager  │                              │  *.tar files    │
│    .log         │                              │                 │
│ backup_service  │                              │                 │
│    .log         │                              │                 │
└─────────────────┘                              └─────────────────┘
```

## ✨ Fonctionnalités

- **Gestion des planifications** : Créer, lister et supprimer des tâches de sauvegarde
- **Service automatisé** : Exécution en arrière-plan avec vérification périodique des horaires
- **Sauvegardes compressées** : Création d'archives .tar des dossiers/fichiers
- **Logging complet** : Traçabilité de toutes les actions et erreurs
- **Interface en ligne de commande** : Contrôle simple via arguments CLI

## 🚀 Installation locale

### Prérequis

- Python 3.6+
- Système Unix/Linux (pour les commandes système)

### Étapes d'installation

1. **Cloner le projet**
   ```bash
   git clone <votre-repo>
   cd backup-system
   ```

2. **Créer la structure des dossiers**
   ```bash
   mkdir -p logs backups
   ```

3. **Vérifier la structure**
   ```bash
   ls -la
   # Vous devriez voir :
   # backup_manager.py
   # backup_service.py
   # backup_schedules.txt (créé automatiquement)
   # logs/
   # backups/
   ```

## 💻 Utilisation

### Commandes disponibles

#### Démarrer le service de sauvegarde
```bash
python3 backup_manager.py start
```

#### Arrêter le service
```bash
python3 backup_manager.py stop
```

#### Créer une nouvelle planification
```bash
python3 backup_manager.py create "chemin/vers/dossier;16:30;nom_sauvegarde"
```

#### Lister les planifications
```bash
python3 backup_manager.py list
```

#### Supprimer une planification
```bash
python3 backup_manager.py delete 0  # Supprime la planification à l'index 0
```

#### Lister les sauvegardes existantes
```bash
python3 backup_manager.py backups
```

### Format des planifications

Les planifications suivent le format : `chemin;heure:minute;nom_sauvegarde`

Exemples :
- `./documents;14:30;docs_backup`
- `/home/user/photos;02:00;photos_daily`
- `./projet;23:59;projet_nightly`

## 🐳 Déploiement Docker

### 1. Créer le Dockerfile

```dockerfile
FROM python:3.9-slim

# Installer les dépendances système
RUN apt-get update && apt-get install -y \
    procps \
    && rm -rf /var/lib/apt/lists/*

# Créer le répertoire de travail
WORKDIR /app

# Copier les fichiers du projet
COPY backup_manager.py .
COPY backup_service.py .

# Créer les dossiers nécessaires
RUN mkdir -p logs backups

# Créer un utilisateur non-root
RUN useradd -m backupuser && chown -R backupuser:backupuser /app
USER backupuser

# Point d'entrée
CMD ["python3", "backup_manager.py"]
```

### 2. Créer le docker-compose.yml

```yaml
version: '3.8'

services:
  backup-system:
    build: .
    container_name: backup-system
    volumes:
      - ./data:/app/data:ro          # Dossiers à sauvegarder (lecture seule)
      - ./backups:/app/backups       # Stockage des sauvegardes
      - ./logs:/app/logs             # Logs persistants
      - ./backup_schedules.txt:/app/backup_schedules.txt  # Configuration
    restart: unless-stopped
    environment:
      - TZ=Europe/Paris
```

### 3. Instructions de déploiement

#### Construction et démarrage
```bash
# Construire l'image Docker
docker-compose build

# Démarrer le conteneur
docker-compose up -d

# Vérifier le statut
docker-compose ps
```

#### Gestion des planifications dans Docker
```bash
# Créer une planification
docker-compose exec backup-system python3 backup_manager.py create "data/documents;14:00;docs_backup"

# Lister les planifications
docker-compose exec backup-system python3 backup_manager.py list

# Démarrer le service
docker-compose exec backup-system python3 backup_manager.py start

# Voir les logs
docker-compose logs -f backup-system
```

#### Accès aux fichiers
```bash
# Voir les logs du manager
docker-compose exec backup-system cat logs/backup_manager.log

# Voir les logs du service
docker-compose exec backup-system cat logs/backup_service.log

# Lister les sauvegardes créées
docker-compose exec backup-system ls -la backups/
```

## 📁 Structure du projet

```
backup-system/
├── backup_manager.py          # Script principal de gestion
├── backup_service.py          # Service de sauvegarde automatisé
├── backup_schedules.txt       # Fichier de configuration des planifications
├── logs/                      # Dossier des logs
│   ├── backup_manager.log     # Logs du gestionnaire
│   └── backup_service.log     # Logs du service
├── backups/                   # Dossier des sauvegardes créées
│   └── *.tar                  # Archives de sauvegarde
├── Dockerfile                 # Configuration Docker
├── docker-compose.yml         # Orchestration Docker
└── README.md                  # Documentation
```

## 📝 Exemples

### Exemple complet d'utilisation

```bash
# 1. Créer plusieurs planifications
python3 backup_manager.py create "documents;09:00;docs_morning"
python3 backup_manager.py create "photos;18:30;photos_evening"
python3 backup_manager.py create "code;23:59;code_nightly"

# 2. Vérifier les planifications
python3 backup_manager.py list

# 3. Démarrer le service
python3 backup_manager.py start

# 4. Attendre l'exécution des sauvegardes...

# 5. Vérifier les sauvegardes créées
python3 backup_manager.py backups

# 6. Consulter les logs
cat logs/backup_manager.log
cat logs/backup_service.log

# 7. Arrêter le service
python3 backup_manager.py stop
```

### Sortie attendue

```
--> Create 3 new schedules
--> Instruction list
0: documents;09:00;docs_morning
1: photos;18:30;photos_evening
2: code;23:59;code_nightly
--> Instruction backups
docs_morning.tar
photos_evening.tar
code_nightly.tar
```

## 🔧 Dépannage

### Problèmes courants

1. **Service ne démarre pas**
   - Vérifier que Python 3 est installé
   - Vérifier les permissions d'écriture dans les dossiers logs/ et backups/

2. **Sauvegardes non créées**
   - Vérifier que les chemins dans backup_schedules.txt existent
   - Consulter les logs pour les erreurs détaillées

3. **Docker : volumes non montés**
   - Vérifier les chemins dans docker-compose.yml
   - S'assurer que les dossiers existent sur l'hôte

### Logs utiles

```bash
# Logs en temps réel
tail -f logs/backup_service.log

# Rechercher des erreurs
grep "Error" logs/*.log

# Docker logs
docker-compose logs --tail=50 backup-system
```
