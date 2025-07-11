#!/usr/bin/env python3


import os
import time
import tarfile

from datetime import datetime

# Configuration des chemins
LOGS = "./logs"
BACKUPS= "./backups"
SCHEDULES_FILE = "backup_schedules.txt"
LOG_FILE = os.path.join(LOGS, "backup_service.log")

def ensure_directories():
#Crée les répertoires nécessaires s'ils n'existent pas
#logs & backup

    os.makedirs(LOGS, exist_ok=True)
    os.makedirs(BACKUPS, exist_ok=True)

def log_message(message):
    
    # Écrit un message dans le fichier de log avec timestamp"""
    # la date avec le message
    timestamp = datetime.now().strftime("[%d/%m/%Y %H:%M]")
    log_entry = f"{timestamp} {message}\n"
    #utilisation de try except pour afficher lerreur 
    try:
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(log_entry)
    except Exception as e:
        print(f"Erreur lors de l'écriture du log: {e}")

def read_schedules():
    """Lit les planifications depuis backup_schedules.txt"""
    schedules = [] # Liste qui va contenir les planifications lues depuis le fichier
    try:
           # Vérifie si le fichier de planification existe avant d'essayer de l'ouvrir
        if os.path.exists(SCHEDULES_FILE):
            with open(SCHEDULES_FILE, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip() # Supprime les espaces et sauts de ligne en début/fin
                    if line:  # Ignore les lignes vides
                        schedules.append(line)  # Ajoute la ligne non vide à la liste
    except Exception as e:
         # En cas d'erreur (ex: fichier inaccessible), enregistre un message d'erreur
        log_message(f"Error reading schedules: {e}")
    
    return schedules # Retourne la liste des planifications lues
def parse_schedule(schedule):
    """Parse une planification au format: path_to_save;time(hh:mm);backup_name"""
    try:
        # Sépare la chaîne en 3 parties attendues : chemin, heure et nom de sauvegarde
        parts = schedule.split(';')
        if len(parts) != 3:
            return None  # Format invalide, on retourne None
        
        path_to_save, time_str, backup_name = parts
        
        # Sépare la partie heure au format hh:mm
        time_parts = time_str.split(':')
        if len(time_parts) != 2:
            return None  # Format de l'heure invalide
        
        # Convertit les heures et minutes en entiers
        hour = int(time_parts[0])
        minute = int(time_parts[1])
        
        # Retourne un dictionnaire structuré avec les données extraites
        return {
            'path': path_to_save.strip(),       # Nettoie les espaces éventuels
            'hour': hour,
            'minute': minute,
            'backup_name': backup_name.strip()  # Nettoie aussi les espaces ici
        }
    
    except Exception:
        return None  # Si une erreur survient (ex: conversion en int échoue), retourne None


def create_backup(source_path, backup_name):
    """Crée une sauvegarde tar du répertoire source"""
    try:
        # Chemin de destination
        backup_path = os.path.join(BACKUPS, f"{backup_name}.tar")
        
        # Vérifie si le répertoire source existe
        if not os.path.exists(source_path):
            log_message(f"Error: source path {source_path} does not exist")
            return False
        
        # Crée l'archive tar
        with tarfile.open(backup_path, "w") as tar:
            if os.path.isdir(source_path):
                # Si c'est un répertoire, ajoute tout son contenu
                for root, dirs, files in os.walk(source_path):
                    for file in files:
                        file_path = os.path.join(root, file)
                        # Utilise un nom relatif dans l'archive
                        arcname = os.path.relpath(file_path, source_path)
                        tar.add(file_path, arcname=arcname)
            else:
                # Si c'est un fichier, l'ajoute directement
                tar.add(source_path, arcname=os.path.basename(source_path))
        
        log_message(f"Backup done for {source_path} in backups/{backup_name}.tar")
        return True
        
    except Exception as e:
        log_message(f"Error creating backup for {source_path}: {e}")
        return False

def create_test_directories():
    """Crée des répertoires de test pour la démonstration"""
    test_dirs = ["test", "test1", "test2"]
    
    for dir_name in test_dirs:
        if not os.path.exists(dir_name):
            os.makedirs(dir_name)
            # Crée quelques fichiers de test
            with open(os.path.join(dir_name, "fichier1.txt"), "w") as f:
                f.write(f"Contenu de test pour {dir_name}")
            with open(os.path.join(dir_name, "fichier2.txt"), "w") as f:
                f.write(f"Autre fichier de test pour {dir_name}")
            log_message(f"Created test directory: {dir_name}")
    
    return test_dirs

def should_backup(schedule_hour, schedule_minute, current_time):
    """Vérifie si une sauvegarde doit être effectuée maintenant"""
    return (current_time.hour == schedule_hour and 
            current_time.minute == schedule_minute)

def process_schedules():
    """Traite toutes les planifications et effectue les sauvegardes nécessaires"""
    current_time = datetime.now()
    schedules = read_schedules()
    
    for schedule_str in schedules:
        schedule = parse_schedule(schedule_str)
        if schedule is None:
            log_message(f"Error: malformed schedule: {schedule_str}")
            continue
        
        # Vérifie si c'est le moment de faire la sauvegarde
        if should_backup(schedule['hour'], schedule['minute'], current_time):
            create_backup(schedule['path'], schedule['backup_name'])

def main():
    """Fonction principale - boucle infinie du service"""
    ensure_directories()
    
    # Crée les répertoires de test si nécessaire
    create_test_directories()
    
    try:
        while True:
            try:
                # Traite les planifications
                process_schedules()
                
                # Attend 45 secondes avant le prochain cycle
                time.sleep(45)
                
            except KeyboardInterrupt:
                log_message("Service stopped by user")
                break
            except Exception as e:
                log_message(f"Error in main loop: {e}")
                # Continue même en cas d'erreur
                time.sleep(45)
                
    except Exception as e:
        log_message(f"Fatal error: {e}")

if __name__ == "__main__":
    main()