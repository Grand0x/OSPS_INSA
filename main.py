import os
import sys
import mmap
import time
import signal
import select

# Chemins des tubes nommés
DWTUBE_PATH = "dwtube1"
WDTUBE_PATH = "wdtube1"
PING_PONG_LIMIT = 5
WATCHDOG_PING_TIMEOUT = 5

# Temps (en secondes) que le watchdog attend avant de considérer qu'il n'y a pas de communication
NO_COMMUNICATION_LIMIT = 3


def create_named_pipes():
  """Crée les tubes nommés si nécessaire."""
  if not os.path.exists(DWTUBE_PATH):
    os.mkfifo(DWTUBE_PATH)
  if not os.path.exists(WDTUBE_PATH):
    os.mkfifo(WDTUBE_PATH)


def send_watchdog_ping_and_wait():
  """
  Envoie un "watchdog_ping" via le tube et attend un "watchdog_pong" en retour.
  """
  # Envoyer un watchdog_ping
  with open(DWTUBE_PATH, 'w') as dwtube:
    dwtube.write("watchdog_ping")
    dwtube.flush()

  # Attendre un watchdog_pong avec une lecture non bloquante
  start_time = time.time()
  with open(WDTUBE_PATH, 'r') as wdtube:
    while (time.time() - start_time) < WATCHDOG_PING_TIMEOUT:
      ready, _, _ = select.select([wdtube], [], [], 0.1)
      if 0 < len(ready):
        message = wdtube.read()
        if message == "watchdog_pong":
          print("return TRUE")
          return True
  return False


def watchdog_process():
  """Processus de surveillance (watchdog)."""
  print("[WATCHDOG] Watchdog démarré.")
  create_named_pipes()

  pid = os.fork()
  if pid == 0:
    main_with_pipes()
    sys.exit(0)
  elif pid < 0:
    print("fork() failed in watchdog")
    sys.exit(-1)
  else:
    time.sleep(2)  # pour laisser le temps au serveur de se lancer
    no_communication_count = 0
    while True:
      if not send_watchdog_ping_and_wait():
        no_communication_count += 1
        print(
            f"[WATCHDOG] Watchdog n'a pas reçu de communication pendant {NO_COMMUNICATION_LIMIT} secondes."
        )
        if no_communication_count >= NO_COMMUNICATION_LIMIT:
          print("[WATCHDOG] Pas de réponse. Redémarrage du serveur principal.")
          os.kill(pid, signal.SIGTERM)
          pid = os.fork()
          if pid == 0:
            main_with_pipes()
            sys.exit(0)
          elif pid < 0:
            print("fork() failed in watchdog retry")
            sys.exit(-1)
          no_communication_count = 0
      else:
        no_communication_count = 0
      time.sleep(1)


def main_with_pipes():
  """Gère la communication entre le serveur principal et secondaire."""
  print("[MAIN] Serveur principal démarré.")
  with mmap.mmap(-1, 10) as shared_memory:
    pid = os.fork()
    if pid == 0:
      print("[SECONDARY] Serveur secondaire démarré.")
      for i in range(PING_PONG_LIMIT):
        with open(DWTUBE_PATH, 'r') as dwtube:
          message = dwtube.read()
          if message == "ping_sent":
            if i == 3:
              print("fake server block (5s)")
              time.sleep(5)
            print("[SECONDARY] Ping reçu. Envoi de pong.")
            shared_memory.seek(0)
            shared_memory.write(b"pong")
            with open(WDTUBE_PATH, 'w') as wdtube:
              wdtube.write("pong_sent")
              wdtube.flush()
          elif message == "watchdog_ping":
            with open(WDTUBE_PATH, 'w') as wdtube:
              wdtube.write("watchdog_pong")
              wdtube.flush()
      print("[SECONDARY] Serveur secondaire terminé.")
      sys.exit(0)
    elif pid < 0:
      print("fork() failed in main")
      sys.exit(-1)
    else:
      for _ in range(PING_PONG_LIMIT):
        shared_memory.seek(0)
        shared_memory.write(b"ping")
        print("[MAIN] Ping envoyé.")
        with open(DWTUBE_PATH, 'w') as dwtube:
          dwtube.write("ping_sent")
          dwtube.flush()
        with open(WDTUBE_PATH, 'r') as wdtube:
          message = wdtube.read()
        if message == "pong_sent":
          print("[MAIN] Pong reçu.")
      os.wait()
      print("[MAIN] Serveur principal terminé.")


if __name__ == '__main__':
  watchdog_process()
