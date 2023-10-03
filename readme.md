# Début du projet OSPS

## Crée par
Robin Juan & Maxime Guiot
FISA 4 INFO
INSA HDF

### Projet OSPS
Le but de ce « TP » est de construire les premières étapes du client(s)-serveur(s), à réaliser en Python 3 en guise de
projet, en mettant en œuvre un certain nombre d’éléments étudiés dans le cours de système et programmation
sécurisée…
Basez-vous sur les exemples placés sur Moodle (des compléments seront fournis en cours de projet).
N’oubliez pas de traiter les codes de retour et exceptions à tous les niveaux.

### Architecture utilisée
Afin de réaliser ce projet dans de bonnes conditions, nous avons opté pour une collaboration de travail directement avec l'outil en ligne " replit.com ".
Cet outil nous permet de travailler en simultané sur le même code, et de pouvoir le tester en temps réel.

De plus, nous avons déclaré le projet dans un repository GitHub. Cet outil nous permettra uniquement de faire des sauvegardes de notre projet en "version", et de pouvoir le partager facilement avec notre encadrant.

### 1. Mise en place d’un segment mémoire partagé entre un serveur principal et un serveur secondaire
Pour manipuler un segment mémoire partagé en Python 3, le module recommandé est multiprocessing. Ce module offre une manière simple et efficace de créer des processus parallèles et de partager des données entre eux.

En particulier, le sous-module multiprocessing.shared_memory fournit une classe SharedMemory qui permet de créer et d'accéder à un segment mémoire partagé. Ce segment peut être utilisé pour partager des données entre plusieurs processus.

Pour créer un segment mémoire partagé, il suffit d'appeler la fonction SharedMemory() en lui passant en paramètre le nom du segment et sa taille. Le nom du segment doit être unique et ne doit pas contenir de caractères spéciaux. La taille du segment doit être un multiple de 8.

Une fois le segment créé, il est possible d'y accéder depuis un autre processus en appelant la fonction SharedMemory() en lui passant en paramètre le nom du segment. Cette fonction retourne un objet SharedMemory qui permet d'accéder au segment mémoire partagé.

### 2. Utilisation d’une paire de tubes nommés pour assurer la synchronisation entre le serveur principal et le serveur secondaire
#### Quel serveur doit s’arrêter en premier pour éviter les zombies ? Qu’est ce qu’un zombie au sens informatique / système d’opération ?

Un processus "zombie" est un processus qui a terminé son exécution (via l'appel système exit) mais dont l'entrée subsiste toujours dans la table des processus, car le processus parent n'a pas encore lu l'état de sortie du processus enfant via wait() ou waitpid(). Cela signifie que le processus enfant a terminé son exécution, mais ses ressources systèmes, notamment sa PID (ID de processus) et son code de sortie, sont encore conservés dans le système jusqu'à ce que le processus parent récupère ces informations.

Pour éviter les processus zombies :
Le processus parent doit toujours appeler wait() ou waitpid() pour récupérer l'état de sortie de ses processus enfants.
Si le processus parent termine avant le processus enfant, le processus enfant est "adopté" par le processus init (le processus avec PID 1), qui appellera wait() pour éviter que le processus enfant devienne un zombie.

Dans le contexte de votre projet avec un serveur principal ("d") et un serveur secondaire ("w") :
Le serveur principal (le processus parent) doit s'assurer de toujours appeler wait() pour récupérer l'état de sortie du serveur secondaire (le processus enfant) une fois que ce dernier a terminé.
Par conséquent, pour éviter les zombies, le serveur secondaire ("w") devrait se terminer en premier, suivi du serveur principal ("d").

Résumé:
Pour éviter les zombies, le serveur secondaire ("w") doit se terminer en premier.
Un "zombie" est un processus qui a terminé son exécution mais dont l'entrée subsiste toujours dans la table des processus, car le processus parent n'a pas encore lu l'état de sortie du processus enfant.

### 3.