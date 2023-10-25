import os
import signal
import time


def parent_signal_handler(signum, frame):
  """Handler for signals received by the parent process."""
  if signum == signal.SIGUSR2:
    print("[PARENT] Received SIGUSR2 from child.")


def child_signal_handler(signum, frame):
  """Handler for signals received by the child process."""
  if signum == signal.SIGUSR1:
    print("[CHILD] Received SIGUSR1 from parent.")
    print("[CHILD] Sending SIGUSR2 to parent.")
    os.kill(os.getppid(), signal.SIGUSR2)


def main():
  """Main function."""
  pid = os.fork()
  if pid < 0:
    print("[MAIN] Error forking child process.")
    return
  if pid == 0:  # Child process
    print("[CHILD] Child process started with PID:", os.getpid())
    signal.signal(signal.SIGUSR1, child_signal_handler)
    while True:
      # Let the child process keep running to receive signals
      time.sleep(1)
  else:  # Parent process
    print("[PARENT] Parent process started with PID:", os.getpid())
    print("[PARENT] Child process has PID:", pid)
    signal.signal(signal.SIGUSR2, parent_signal_handler)
    time.sleep(2)  # Give the child some time to set up its signal handler
    print("[PARENT] Sending SIGUSR1 to child.")
    os.kill(pid, signal.SIGUSR1)
    while True:
      # Let the parent process keep running to receive signals
      time.sleep(1)


if __name__ == '__main__':
  main()
