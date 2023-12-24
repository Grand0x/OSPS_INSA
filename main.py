import os
import sys
import mmap
import time
import select
import threading
import signal

# Chemins des tubes nommés
DWTUBE_PATH = "dwtube1"
WDTUBE_PATH = "wdtube1"
PING_PONG_LIMIT = 5
WATCHDOG_PING_TIMEOUT = 5

# Temps (en secondes) que le watchdog attend avant de considérer qu'il n'y a pas de communication
NO_COMMUNICATION_LIMIT = 3

# Création des verrous pour les tubes
dwtube_lock = threading.Lock()
wdtube_lock = threading.Lock()


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
  with dwtube_lock:
    with open(DWTUBE_PATH, 'w') as dwtube:
      dwtube.write("watchdog_ping")
      dwtube.flush()
      dwtube.close()

  # Attendre un watchdog_pong avec une lecture non bloquante
  start_time = time.time()
  with wdtube_lock:
    with open(WDTUBE_PATH, 'r') as wdtube:
      while (time.time() - start_time) < WATCHDOG_PING_TIMEOUT:
        ready, _, _ = select.select([wdtube], [], [], 0.5)
        if 0 < len(ready):
          message = wdtube.read()
          if message == "watchdog_pong":
            return True
      wdtube.close()
  return False


def read_with_select(pipe_path, lock, timeout_duration):
  with lock:  # Acquérir le verrou avant de lire le tube
    with open(pipe_path, 'r') as pipe:
      ready, _, _ = select.select([pipe], [], [], timeout_duration)
      if ready:
        return pipe.read()
      pipe.close()
  return None


def watchdog_process():
  """Processus de surveillance (watchdog)."""
  print("[WATCHDOG] Watchdog démarré.")
  create_named_pipes()

  pid = os.fork()
  if pid == 0:
    main_with_pipes()
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
            f"[WATCHDOG] Watchdog n'a pas reçu de communication pendant {no_communication_count*WATCHDOG_PING_TIMEOUT} secondes."
        )
        if no_communication_count >= NO_COMMUNICATION_LIMIT:
          print("[WATCHDOG] Pas de réponse. Redémarrage du serveur principal.")
          os.kill(pid, signal.SIGTERM)
          pid = os.fork()
          if pid == 0:
            main_with_pipes()
            print("[WATCHDOG] Watchdog terminé.")
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
      ping_pong_count = 0
      while True:
        if ping_pong_count >= PING_PONG_LIMIT:
          break
        message = read_with_select(DWTUBE_PATH, dwtube_lock, 1)
        if message == "ping_sent":
          print("[SECONDARY] Ping reçu. Envoi de pong.")
          shared_memory.seek(0)
          shared_memory.write(b"pong")
          with wdtube_lock:
            with open(WDTUBE_PATH, 'w') as wdtube:
              wdtube.write("pong_sent")
              wdtube.flush()
              ping_pong_count += 1
              wdtube.close()
        elif message == "watchdog_ping":
          with wdtube_lock:
            with open(WDTUBE_PATH, 'w') as wdtube:
              wdtube.write("watchdog_pong")
              wdtube.flush()
              wdtube.close()
      print("[SECONDARY] Serveur secondaire terminé.")
      sys.exit(0)
    elif pid < 0:
      print("fork() failed in main")
      sys.exit(-1)
    else:
      time.sleep(2)
      ping_pong_count = 0
      shared_memory.seek(0)
      shared_memory.write(b"ping")
      with dwtube_lock:
        with open(DWTUBE_PATH, 'w') as dwtube:
          dwtube.write("ping_sent")
          dwtube.flush()
          dwtube.close()
          ping_pong_count += 1
          print("[MAIN] Ping envoyé.")
      while True:
        if ping_pong_count >= PING_PONG_LIMIT:
          break
        message = read_with_select(WDTUBE_PATH, wdtube_lock, 1)
        if message == "pong_sent":
          print("[MAIN] Pong reçu.")
          shared_memory.seek(0)
          shared_memory.write(b"ping")
          with dwtube_lock:
            with open(DWTUBE_PATH, 'w') as dwtube:
              dwtube.write("ping_sent")
              dwtube.flush()
              dwtube.close()
              ping_pong_count += 1
              print("[MAIN] Ping envoyé.")
        elif message == "watchdog_ping":
          with wdtube_lock:
            with open(DWTUBE_PATH, 'w') as wdtube:
              wdtube.write("watchdog_pong")
              wdtube.flush()
              wdtube.close()
      os.wait()
      print("[MAIN] Serveur principal terminé.")


if __name__ == '__main__':
  watchdog_process()
