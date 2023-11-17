import socket

SERVER_IP = '127.0.0.1'
MAIN_PORT = 2222
BUFFER_SIZE = 1024

def main():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((SERVER_IP, MAIN_PORT))
    print("[CLIENT] Connecté au serveur principal")

    while True:
        request_type = input("[CLIENT] Entrez le type de requête (requetetype1/requetetype2): ")
        s.sendall(request_type.encode())

        response = s.recv(BUFFER_SIZE).decode()

        if response == "Type de requête inconnu":
            print("[CLIENT] Type de requête inconnu. Veuillez réessayer.")
            continue
        elif response.isdigit():
            secondary_port = int(response)
            s.close()

            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect((SERVER_IP, secondary_port))
            print(f"[CLIENT] Connecté au serveur secondaire sur le port {secondary_port}")

            data = input("[CLIENT] Entrez les données à envoyer au serveur secondaire: ")
            s.sendall(data.encode())

            response = s.recv(BUFFER_SIZE).decode()
            print(f"[CLIENT] Réponse du serveur secondaire: {response}")
            break
        else:
            print(f"[CLIENT] Erreur: {response}")
            break

    s.close()

if __name__ == "__main__":
    main()
