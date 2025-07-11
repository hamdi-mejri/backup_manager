#!/usr/bin/env python3
import sys
import os
import subprocess
import datetime
import signal


# vérification que les dossiers contenant les logs 
# et les backups existent en regardant les chemins,
# s'ils n'existent pas on les créée 
def verification_dossier():
    if not os.path.exists('./logs'):
        os.makedirs('./logs')
    if not os.path.exists('./backups'):
        os.makedirs('./backups')

# formatage au bon format temps d'un message
# puis enregistrement 
# dans le fichier de log backup_manager
def log_message(message):
    timestamp = datetime.datetime.now().strftime("%d/%m/%Y %H:%M")
    log_entry = f"[{timestamp}] {message}\n" #f : formatted string literal : permet de mettre variable dans string 
    
    verification_dossier()
    with open('./logs/backup_manager.log', 'a') as log_file: #'a' : append
        log_file.write(log_entry)

# récupération de pid de backup_service 
# en listant tous les processus actifs au full format
def get_backup_service_pid():
    try:
        result = subprocess.run(['ps', '-A', '-f'], capture_output=True, text=True)
        for line in result.stdout.split('\n'):
            if 'backup_service.py' in line and 'python' in line:
                parts = line.split()
                return int(parts[1])  # le PID est sur la seconde colonne de la commande terminal précédent
    except:
        pass
    return None


# on récupère le pid avec la fonction précédente
# si on trouve le pid cela veut dire que le processus 
# est deja en fonctionnement et on renvoie une erreur 
# sinon on le run avec subprocess et si on y arrive pas
# on renvoie une erreur
def start_backup_service():
    try:
        pid = get_backup_service_pid()
        if pid:
            log_message("Error: backup_service fonctionne deja")
            return
        
        subprocess.Popen(['python3', './backup_service.py'], start_new_session=True) #popen est comme run mais en asynchrone, il n'est pas bloquant 
        log_message("backup_service started")
    except Exception as e:
        log_message("Error: can't start backup_service")

# on récupère le pid avec la fonction précédente
# si on ne trouve pas le pid cela veut dire que le processus 
# ne fonctionne pas et on renvoie une erreur 
# sinon on le kill, si le kill ne fonctionne pas 
# on renvoie une erreur
def stop_backup_service():
    try:
        pid = get_backup_service_pid()
        if not pid:
            log_message("Error: backup_service not running")
            return
        
        os.kill(pid, signal.SIGTERM) #signal de terminaison propre 
        log_message("backup_service stopped")
    except Exception as e:
        log_message("Error: can't stop backup_service")

# on vérifie le format du schedule en arg si ça ne nous correspond pas
# on renvoie une erreur
# on vérifie qu'on a bien l'heure au bon format hh:mm
# on vérifie que l'heure est bien comprise entre 0 et 23 
# et les minutes entre 0 et 59 sinon on renvoie une erreur
# on ajoute le schedule au backup_schedules.txt
# on appelle log_message pour enregistrer dans le log de backup_manager
def create_schedule(schedule_string):
    try:
        # Format schedule valide: file_name;hour:minutes;backup_file_name
        parts = schedule_string.split(';')
        if len(parts) != 3 or not parts[0] or not parts[1] or not parts[2]:
            log_message(f"Error: malformed schedule: {schedule_string}")
            return
        
        # Format time valide 
        time_parts = parts[1].split(':')
        if len(time_parts) != 2:
            log_message(f"Error: malformed schedule: {schedule_string}")
            return
        
        try:
            hour = int(time_parts[0])
            minute = int(time_parts[1])
            if hour < 0 or hour > 23 or minute < 0 or minute > 59:
                log_message(f"Error: malformed schedule: {schedule_string}")
                return
        except ValueError:
            log_message(f"Error: malformed schedule: {schedule_string}")
            return
        
        # Ajout au back_schedules.txt
        with open('./backup_schedules.txt', 'a') as f:
            f.write(schedule_string + '\n')
        
        log_message(f"New schedule added: {schedule_string}")
    except Exception as e:
        log_message(f"Error: malformed schedule: {schedule_string}")

# on vérifie qu'on peut ouvrir backup_schedules.txt
# si c'est le cas on affiche les lignes du fichier
def list_schedules():
    try:
        log_message("Show schedules list")
        with open('./backup_schedules.txt', 'r') as f:
            lines = f.readlines()
        
        for i, line in enumerate(lines):
            print(f"{i}: {line.strip()}") #on affiche le numéro de ligne suivie du contenu (strip enlève espace et retour ligne)
    except FileNotFoundError:
        log_message("Error: can't find backup_schedules.txt")
    except Exception as e:
        log_message("Error: can't find backup_schedules.txt")

# suppression d'un schedule à un index donné
# on ouvre backup_schedule.txt en 'r'
# on créee une copie dans lines du contenu du backup_schedules.txt
# puis on vérifie que l'index donné est bien correct
# on supprime la ligne à l'index indiqué dans lines on ecrase le contenu ('w') dans backup_schedules.txt
def delete_schedule(index):
    try:
        index = int(index)
        with open('./backup_schedules.txt', 'r') as f:
            lines = f.readlines()
        
        if index < 0 or index >= len(lines):
            log_message(f"Error: can't find schedule at index {index}")
            return
        
        del lines[index]
        
        with open('./backup_schedules.txt', 'w') as f:
            f.writelines(lines)
        
        log_message(f"Schedule at index {index} deleted")
    except FileNotFoundError:
        log_message("Error: can't find backup_schedules.txt")
    except ValueError:
        log_message(f"Error: can't find schedule at index {index}")
    except Exception as e:
        log_message(f"Error: can't find schedule at index {index}")

# on vérifie si le dossier backup existe sinon erreur
# si le dossier existe on filtres et affiche les TAR
def list_backups():
    try:
        log_message("Show backups list")
        if not os.path.exists('./backups'):
            log_message("Error: can't find backups directory")
            return
        
        files = os.listdir('./backups') #on récupère les fichiers du dossier
        tar_files = [f for f in files if f.endswith('.tar')] #on ne garde que les .tar (list comprehension (opération sur listes (filtrer dance cas)))
        
        for tar_file in tar_files:
            print(tar_file)
    except Exception as e:
        log_message("Error: can't find backups directory")


# on vérifie les arguments
# on récupère la commande
# on traite la commande (s'il y a des paramètres ou des erreurs)
def main():
    if len(sys.argv) < 2:
        print("Usage: python3 backup_manager.py [start|stop|create|list|delete|backups]")
        return
    
    command = sys.argv[1]
    
    if command == "start":
        start_backup_service()
    elif command == "stop":
        stop_backup_service()
    elif command == "create":
        if len(sys.argv) < 3:
            print("Usage: python3 backup_manager.py create [schedule]")
            return
        create_schedule(sys.argv[2])
    elif command == "list":
        list_schedules()
    elif command == "delete":
        if len(sys.argv) < 3:
            print("Usage: python3 backup_manager.py delete [index]")
            return
        delete_schedule(sys.argv[2])
    elif command == "backups":
        list_backups()
    else:
        print("Unknown command. Use: start, stop, create, list, delete, or backups")

if __name__ == "__main__":
    main()