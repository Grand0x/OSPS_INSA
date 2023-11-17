import socket
import os

MAIN_PORT = 2222
SECONDARY_PORT = 2223
BUFFER_SIZE = 1024

DW_PIPE = "/tmp/dwtube1"
WD_PIPE = "/tmp/wdtube1"

# Crée les tubes nommés s'ils n'existent pas
if not os.path.exists(DW_PIPE):
    os.mkfifo(DW_PIPE)
    print("[INFO] Tube nommé dwtube1 créé")
if not os.path.exists(WD_PIPE):
    os.mkfifo(WD_PIPE)
    print("[INFO] Tube nommé wdtube1 créé")

def main_server():
    host = '0.0.0.0'
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind((host, MAIN_PORT))
    s.listen(5)
    print("[MAIN SERVER] En écoute sur le port", MAIN_PORT)

    while True:
        conn, addr = s.accept()
        print(f"[MAIN SERVER] Connexion établie avec {addr}")

        # Réception de la requête du client
        request_type = conn.recv(BUFFER_SIZE).decode()
        print(f"[MAIN SERVER] Requête reçue: {request_type}")

        while True:  # Ajout d'une boucle pour permettre de multiples tentatives
            # Délégation au serveur secondaire via le tube
            with open(DW_PIPE, 'w') as dw_pipe:
                dw_pipe.write(request_type)
            print("[MAIN SERVER] Message écrit dans le tube dwtube1")

            # Attente de la réponse du serveur secondaire
            with open(WD_PIPE, 'r') as wd_pipe:
                response = wd_pipe.readline()
            print("[MAIN SERVER] Message lu du tube wdtube1")

            if response == "debuttraitement":
                conn.sendall(str(SECONDARY_PORT).encode())
                print("[MAIN SERVER] Port du serveur secondaire envoyé au client")
                
                # Attente de la fin du traitement du serveur secondaire
                with open(WD_PIPE, 'r') as wd_pipe:
                    end_response = wd_pipe.readline()
                if end_response == "fintraitement":
                    print("[MAIN SERVER] Traitement terminé par le serveur secondaire")
                break  # Sort de la boucle après avoir traité la requête
            elif response == "errortype":
                conn.sendall("Type de requête inconnu".encode())
                print("[MAIN SERVER] Type de requête inconnu reçu")
                request_type = conn.recv(BUFFER_SIZE).decode()  # Attente d'une nouvelle tentative du client
                print(f"[MAIN SERVER] Nouvelle requête reçue: {request_type}")
            elif response == "errtraitement":
                conn.sendall("Erreur lors du traitement".encode())
                print("[MAIN SERVER] Erreur signalée par le serveur secondaire")
                break  # Sort de la boucle en cas d'erreur de traitement

        conn.close()  # Ferme la connexion après avoir quitté la boucle
        print("[MAIN SERVER] Connexion avec le client fermée")

def secondary_server():
    host = '0.0.0.0'
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind((host, SECONDARY_PORT))
    s.listen(5)
    print("[SECONDARY SERVER] En écoute sur le port", SECONDARY_PORT)

    while True:
        # Lecture de la requête du tube dwtube1
        with open(DW_PIPE, 'r') as dw_pipe:
            request_type = dw_pipe.readline().strip()
        print("[SECONDARY SERVER] Message lu du tube dwtube1")

        if os.path.exists(DW_PIPE):
            os.remove(DW_PIPE)  # Supprime le tube après la lecture
        os.mkfifo(DW_PIPE)  # Recrée le tube pour la prochaine lecture

        if request_type in ["requetetype1", "requetetype2"]:
            print(f"[SECONDARY SERVER] Requête reçue: {request_type}")

            # Informe le serveur principal du début du traitement
            with open(WD_PIPE, 'w') as wd_pipe:
                wd_pipe.write("debuttraitement")
            print("[SECONDARY SERVER] Message écrit dans le tube wdtube1")

            conn, addr = s.accept()
            print(f"[SECONDARY SERVER] Connexion établie avec {addr}")

            # Réception des données du client
            data = conn.recv(BUFFER_SIZE).decode()
            print(f"[SECONDARY SERVER] Data reçue: {data}")

            # Traite la requête et renvoie une réponse
            response = "Recu !"
            conn.sendall(response.encode())
            with open(WD_PIPE, 'w') as wd_pipe:
                wd_pipe.write("fintraitement")
            print("[SECONDARY SERVER] Message écrit dans le tube wdtube1")

            conn.close()
            print("[SECONDARY SERVER] Connexion avec le client fermée")
        else:
            print(f"[SECONDARY SERVER] Requête inconnue: {request_type}")
            with open(WD_PIPE, 'w') as wd_pipe:
                wd_pipe.write("errortype")
            print("[SECONDARY SERVER] Message d'erreur écrit dans le tube wdtube1")

if __name__ == "__main__":
    pid = os.fork()
    if pid < 0:
        print("[ERROR] Le fork a échoué")
    elif pid == 0:
        secondary_server()
    else:
        main_server()
