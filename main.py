import os
import sys
import mmap

# Chemins des tubes nommés
DWTUBE_PATH = "dwtube1"
WDTUBE_PATH = "wdtube1"
PING_PONG_LIMIT = 14


def create_named_pipes():
  """
    Crée les tubes nommés si nécessaire.
    """
  if not os.path.exists(DWTUBE_PATH):
    os.mkfifo(DWTUBE_PATH)
  if not os.path.exists(WDTUBE_PATH):
    os.mkfifo(WDTUBE_PATH)


def watchdog_process():
  """
    Processus de surveillance (watchdog). 
    Lance le serveur principal et le surveille.
    """
  print("[WATCHDOG] Watchdog démarré.")

  if not os.path.exists(WDTUBE_PATH):
    os.mkfifo(WDTUBE_PATH)

  pid = os.fork()
  if pid == 0:
    main_with_pipes()
    sys.exit(0)
  else:
    while True:
      with open(WDTUBE_PATH, 'r') as wdtube:
        msg = wdtube.read()
        if msg == "exit":
          break

  print("[WATCHDOG] Watchdog terminé.")


def main_with_pipes():
  """
    Gère la communication entre le serveur principal et secondaire.
    """
  print("[MAIN] Serveur principal démarré.")
  create_named_pipes()

  with mmap.mmap(-1, 10) as shared_memory:
    pid = os.fork()
    if pid == 0:
      print("[SECONDARY] Serveur secondaire démarré.")
      for _ in range(PING_PONG_LIMIT):
        with open(DWTUBE_PATH, 'r') as dwtube:
          dwtube.read()
        if shared_memory[:4].decode('utf-8') == "ping":
          print("[SECONDARY] Ping reçu. Envoi de pong.")
          shared_memory.seek(0)
          shared_memory.write(b"pong")
          with open(WDTUBE_PATH, 'w') as wdtube:
            wdtube.write("pong_sent")
            wdtube.flush()
      print("[SECONDARY] Serveur secondaire terminé.")
      sys.exit(0)
    else:
      for _ in range(PING_PONG_LIMIT):
        shared_memory.seek(0)
        shared_memory.write(b"ping")
        print("[MAIN] Ping envoyé.")
        with open(DWTUBE_PATH, 'w') as dwtube:
          dwtube.write("ping_sent")
          dwtube.flush()
        with open(WDTUBE_PATH, 'r') as wdtube:
          wdtube.read()
        if shared_memory[:4].decode('utf-8') == "pong":
          print("[MAIN] Pong reçu.")

      os.wait()  # Attend la fin du serveur secondaire

      with open(WDTUBE_PATH, 'w') as wdtube:
        wdtube.write("exit")
        wdtube.flush()

      print("[MAIN] Serveur principal terminé.")


if __name__ == '__main__':
  watchdog_process()
