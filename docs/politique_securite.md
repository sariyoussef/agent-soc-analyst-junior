# Politique de Sécurité Interne - Gestion des Incidents d'Authentification

## 1. Classification des Sévérités
- **Faible** : 1 à 4 échecs de connexion isolés sur une période supérieure à 1 heure. Action : Surveillance passive.
- **Moyenne** : Tentative de force brute détectée (5 à 9 échecs en moins de 10 minutes) sans compromission réussie. Action : Alerte équipe réseau et recommandation de bannissement temporaire de l'IP (24h).
- **Élevée** : Brute-force massif ($\ge 10$ échecs) ou ciblage de comptes à hauts privilèges (root, admin). Action : Recommandation de blocage immédiat de l'IP et audit des sessions actives.
- **Critique** : Brute-force suivi d'une connexion réussie (`Accepted password` ou `Accepted publickey`) depuis la même IP suspecte. Action : Escalade immédiate Niveau 2 (Analyste Senior), isolation de la machine et révocation des credentials compromis.

## 2. Procédure d'Escalade
- Tout incident classé **Critique** doit être transmis sans délai à l'analyste N2 via le canal d'urgence.
- Les actions de blocage d'IP ou de coupure de service réseau ne peuvent être exécutées qu'après validation humaine de l'équipe réseau (aucune action destructive automatisée par l'IA).
