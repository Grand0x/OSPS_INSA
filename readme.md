# OSPS – TP/Projet Python – FISA 4A 2023
## Auteurs
- Robin JUAN
- Maxime GUIOT

## GitHub
- Link : https://github.com/Grand0x/OSPS_INSA
- Main Branch : dev

Nous avons effectué plusieurs releases correspondant aux différentes étapes du projet. 

## Etape 1 - Mise en place d’un segment mémoire partagé entre un serveur principal et un serveur secondaire.
### Commentaires


### Difficultés rencontrées


### Améliorations possibles

## Etape 2 - Utilisation d’une paire de tubes nommés pour assurer la synchronisation
### Commentaires


### Difficultés rencontrées


### Améliorations possibles

## Etape 3 - Mise en place d’un processus (indépendant) de surveillance
### Commentaires


### Difficultés rencontrées


### Améliorations possibles

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