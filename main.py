import os
import time
import sys
import mmap

# Définition des constantes
PING_PONG_LIMIT = 3  # Nombre d'échanges ping-pong avant d'arrêter les serveurs


def main():
  # Créer un segment mémoire partagé avec une taille suffisante pour stocker "ping" ou "pong"
  with mmap.mmap(-1, 10) as shared_memory:
    # Lancement du processus enfant (serveur secondaire "w") via fork
    pid = os.fork()

    if pid == 0:  # Serveur secondaire "w"
      for _ in range(PING_PONG_LIMIT):
        while True:
          # Attente du message "ping" du serveur principal
          if shared_memory[:4].decode('utf-8') == "ping":
            break

        print("Serveur secondaire (w) a reçu 'ping', envoie 'pong'")
        shared_memory.seek(0)
        shared_memory.write(b"pong")
        time.sleep(1)  # Simuler un temps de traitement

      sys.exit(0)  # Arrêt du serveur secondaire après PING_PONG_LIMIT échanges

    else:  # Serveur principal "d"
      for _ in range(PING_PONG_LIMIT):
        shared_memory.seek(0)
        shared_memory.write(b"ping")  # Envoi du message "ping"
        print("Serveur principal (d) envoie 'ping'")

        while True:
          # Attente de la réponse "pong" du serveur secondaire
          if shared_memory[:4].decode('utf-8') == "pong":
            break

        print("Serveur principal (d) a reçu 'pong'")
        time.sleep(1)  # Attendre avant le prochain ping

      os.wait()  # Attendre que le serveur secondaire s'arrête


# Code pour exécuter le programme principal
if __name__ == '__main__':
  main()
