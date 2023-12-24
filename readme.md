# OSPS – TP/Projet Python – FISA 4A 2023
## Auteurs
- Robin JUAN
- Maxime GUIOT

FISA 4 INFO
INSA HDF

## GitHub
- Link : https://github.com/Grand0x/OSPS_INSA
- Main Branch : dev

Nous avons effectué 4 releases correspondant aux différentes étapes du projet. 

## Projet OSPS
Le but de ce « TP » est de construire les premières étapes du client(s)-serveur(s), à réaliser en Python 3 en guise de
projet, en mettant en œuvre un certain nombre d’éléments étudiés dans le cours de système et programmation
sécurisée…
Basez-vous sur les exemples placés sur Moodle (des compléments seront fournis en cours de projet).
N’oubliez pas de traiter les codes de retour et exceptions à tous les niveaux.

## Architecture utilisée
Afin de réaliser ce projet dans de bonnes conditions, nous avons opté pour une collaboration de travail directement avec l'outil en ligne " replit.com ".
Cet outil nous permet de travailler en simultané sur le même code, et de pouvoir le tester en temps réel.

De plus, nous avons déclaré le projet dans un repository GitHub. Cet outil nous permettra uniquement de faire des sauvegardes de notre projet en "version", et de pouvoir le partager facilement avec notre encadrant.

## Etape 1 - Mise en place d’un segment mémoire partagé entre un serveur principal et un serveur secondaire.
### Commentaires
- Se lance sans problème.

### Difficultés rencontrées
- RAS

### Améliorations possibles
- RAS

## Etape 2 - Utilisation d’une paire de tubes nommés pour assurer la synchronisation
### Commentaires
- Mise en place d'une paire de tubes nommés pour la communication et la synchronisation entre le serveur principal et le serveur secondaire.
- Implémentation d'un mécanisme de type "ping-pong" pour tester la communication entre les serveurs.

### Difficultés rencontrées
- Gestion des accès concurrentiels aux tubes nommés, en particulier pour éviter les blocages lors de la lecture/écriture.
- Synchronisation correcte des messages entre les serveurs pour assurer une communication fluide et sans erreur.

### Améliorations possibles
- Optimiser la gestion des tubes pour réduire les risques de blocage et améliorer les performances.
- Améliorer la robustesse du mécanisme de communication pour mieux gérer les cas d'erreur et les scénarios de haute charge.

## Etape 3 - Mise en place d’un processus (indépendant) de surveillance
### Commentaires
- Implémentation d'un processus de surveillance (watchdog) qui vérifie régulièrement la santé du serveur principal.
- Utilisation de tubes nommés supplémentaires pour permettre au watchdog de communiquer avec le serveur principal.

### Difficultés rencontrées
- Assurer que le watchdog ne se bloque pas lorsqu'il attend une réponse du serveur principal.
- Gérer correctement les scénarios où le serveur principal est en panne ou ne répond pas, nécessitant un redémarrage.

### Améliorations possibles
- Renforcer la logique de détection des pannes du serveur principal pour minimiser les faux positifs et les réponses tardives.
- Améliorer la stratégie de redémarrage du serveur principal pour garantir une reprise rapide et sûre des opérations.


## Etape 4 - Ajout d'un client
### Commentaires
- D'abord lancer le ```server.py```, puis le ```client.py```. 
- Le client doit d'abord défnir son type de requête, puis envoie un message au serveur.

### Difficultés rencontrées
- Gestion des tubes nommés
- Gestion des erreurs

### Améliorations possibles
- Gestion des erreurs
- Connexion de plusieurs clients en simultané
- Ajout d'un watchdog
