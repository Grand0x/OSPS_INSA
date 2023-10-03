import os
import time
import sys
import mmap

# Chemins des tubes nommés
DWTUBE_PATH = "dwtube1"
WDTUBE_PATH = "wdtube1"
PING_PONG_LIMIT = 5  # Nombre d'échanges ping-pong avant d'arrêter les serveurs


def create_named_pipes():
  """Créer des tubes nommés s'ils n'existent pas déjà."""
  if not os.path.exists(DWTUBE_PATH):
    os.mkfifo(DWTUBE_PATH)
  if not os.path.exists(WDTUBE_PATH):
    os.mkfifo(WDTUBE_PATH)


def main_with_pipes():
  # Créer les tubes nommés
  create_named_pipes()

  # Créer un segment mémoire partagé
  with mmap.mmap(-1, 10) as shared_memory:
    pid = os.fork()

    if pid == 0:  # Serveur secondaire "w"
      for _ in range(PING_PONG_LIMIT):
        # Attendre une notification du serveur principal via dwtube1
        with open(DWTUBE_PATH, 'r') as dwtube:
          dwtube.read()

        # Vérifier le message "ping" dans le segment mémoire partagé
        if shared_memory[:4].decode('utf-8') == "ping":
          print("Serveur secondaire (w) a reçu 'ping', envoie 'pong'")
          shared_memory.seek(0)
          shared_memory.write(b"pong")

          # Notifier le serveur principal via wdtube1
          with open(WDTUBE_PATH, 'w') as wdtube:
            wdtube.write("pong_sent")
            wdtube.flush()

      sys.exit(0)

    else:  # Serveur principal "d"
      for _ in range(PING_PONG_LIMIT):
        shared_memory.seek(0)
        shared_memory.write(b"ping")  # Envoi du message "ping"
        print("Serveur principal (d) envoie 'ping'")

        # Notifier le serveur secondaire via dwtube1
        with open(DWTUBE_PATH, 'w') as dwtube:
          dwtube.write("ping_sent")
          dwtube.flush()

        # Attendre une notification du serveur secondaire via wdtube1
        with open(WDTUBE_PATH, 'r') as wdtube:
          wdtube.read()

        # Vérifier le message "pong" dans le segment mémoire partagé
        if shared_memory[:4].decode('utf-8') == "pong":
          print("Serveur principal (d) a reçu 'pong'")

      os.wait()

      # Suppression des tubes nommés après utilisation
      os.remove(DWTUBE_PATH)
      os.remove(WDTUBE_PATH)


# Code pour exécuter le programme principal
if __name__ == '__main__':
  main_with_pipes()
