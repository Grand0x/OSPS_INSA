import os
import sys
import mmap
import signal
import time

# Chemins des tubes nommés
DWTUBE_PATH = "dwtube1"
WDTUBE_PATH = "wdtube1"
PING_PONG_LIMIT = 5

# Temps (en secondes) que le watchdog attend avant de considérer qu'il n'y a pas de communication
NO_COMMUNICATION_LIMIT = 3

# Temps (en secondes) que le watchdog attend une réponse après avoir envoyé un SIGUSR1
PING_RESPONSE_TIMEOUT = 5

# Variable pour stocker l'état du ping (répondu ou non)
ping_response_received = False


def create_named_pipes():
  """
    Crée les tubes nommés si nécessaire.
    """
  if not os.path.exists(DWTUBE_PATH):
    os.mkfifo(DWTUBE_PATH)
  if not os.path.exists(WDTUBE_PATH):
    os.mkfifo(WDTUBE_PATH)


def signal_handler(signum, frame):
  """
    Gestionnaire pour les signaux reçus.
    """
  global ping_response_received
  if signum == signal.SIGUSR2:
    ping_response_received = True


def response_to_ping(signum, frame, watchdog_pid):
  """Envoyer un signal SIGUSR2 en réponse à un SIGUSR1."""
  os.kill(watchdog_pid, signal.SIGUSR2)


def send_ping_and_wait(pid):
  """
    Envoie un signal SIGUSR1 (ping) et attend un SIGUSR2 (pong).
    """
  global ping_response_received
  ping_response_received = False
  os.kill(pid, signal.SIGUSR1)
  start_time = time.time()

  while not ping_response_received and (time.time() -
                                        start_time) < PING_RESPONSE_TIMEOUT:
    time.sleep(0.1)

  return ping_response_received


def watchdog_process():
  """Processus de surveillance (watchdog)."""
  print("[WATCHDOG] Watchdog démarré.")
  create_named_pipes()

  pid = os.fork()
  if pid == 0:
    main_with_pipes(os.getpid())  # Passer le PID du watchdog
    sys.exit(0)
  elif pid < 0:
    print("fork() failed in watchdog")
    sys.exit(-1)
  else:
    signal.signal(signal.SIGUSR2, signal_handler)
    time.sleep(2)  #pour laisser le temps au serveur de se lancer
    no_communication_count = 0
    while True:
      if not send_ping_and_wait(pid):
        no_communication_count += 1
        if no_communication_count >= NO_COMMUNICATION_LIMIT:
          print("[WATCHDOG] Pas de réponse. Redémarrage du serveur principal.")
          os.kill(pid, signal.SIGTERM)
          pid = os.fork()
          if pid == 0:
            main_with_pipes(os.getpid())
            sys.exit(0)
          elif pid < 0:
            print("fork() failed in watchdog retry")
            sys.exit(-1)
          no_communication_count = 0
      else:
        no_communication_count = 0
      time.sleep(1)


def main_with_pipes(watchdog_pid):
  """Gère la communication entre le serveur principal et secondaire."""
  print("[MAIN] Serveur principal démarré.")

  # Configurer la réponse aux pings du watchdog
  signal.signal(signal.SIGUSR1,
                lambda s, f: response_to_ping(s, f, watchdog_pid))

  with mmap.mmap(-1, 10) as shared_memory:
    pid = os.fork()
    if pid == 0:
      print("[SECONDARY] Serveur secondaire démarré.")
      for i in range(PING_PONG_LIMIT):
        if i == 3:
          print("fake server block (10s)")
          time.sleep(10)
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
          wdtube.read()
        if shared_memory[:4].decode('utf-8') == "pong":
          print("[MAIN] Pong reçu.")
      os.wait()
      print("[MAIN] Serveur principal terminé.")


if __name__ == '__main__':
  watchdog_process()
