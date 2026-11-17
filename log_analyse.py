import re
from datetime import datetime, timedelta
from typing import List, Dict, Any

def analyser_authlog(chemin_fichier: str) -> List[Dict[str, Any]]:
    """
    Lit un fichier auth.log ligne par ligne et extrait les informations structurées.
    """
    entrees = []
    # Expression régulière pour parser les logs SSH standard
    # Exemple : Oct 24 09:00:17 server sshd[1591]: Failed password for invalid user admin from 203.0.113.45 port 45120 ssh2
    pattern = re.compile(
        r"(?P<mois>[A-Z][a-z]{2})\s+(?P<jour>\d+)\s+(?P<heure>\d{2}:\d{2}:\d{2})\s+"
        r"(?P<hote>\S+)\s+(?P<processus>[^:]+):\s+(?P<message>.*)"
    )

    try:
        with open(chemin_fichier, 'r', encoding='utf-8') as f:
            for ligne in f:
                ligne = ligne.strip()
                if not ligne:
                    continue
                match = pattern.match(ligne)
                if match:
                    data = match.groupdict()
                    # Extraction simplifiée d'IP IPv4 via regex classique
                    ip_v4_match = re.search(r'\b(\d{1,3}(?:\.\d{1,3}){3})\b', data['message'])

                    ip_source = ip_v4_match.group(1) if ip_v4_match else "Inconnue"

                    entrees.append({
                        "timestamp_str": f"{data['mois']} {data['jour']} {data['heure']}",
                        "hote": data['hote'],
                        "processus": data['processus'],
                        "message": data['message'],
                        "ip_source": ip_source,
                        "ligne_brute": ligne
                    })
    except FileNotFoundError:
        print(f"[-] Erreur : Fichier introuvable à l'emplacement {chemin_fichier}")

    return entrees

def detecter_bruteforce(entrees: List[Dict[str, Any]], seuil: int = 5, fenetre_minutes: int = 10) -> List[Dict[str, Any]]:
    """
    Détecte les tentatives de brute-force : au moins [seuil] échecs depuis
    la même IP en moins de [fenetre_minutes] minutes.
    """
    tentatives_echec = {}

    for entree in entrees:
        if "Failed password" in entree["message"] or "Invalid user" in entree["message"]:
            ip = entree["ip_source"]
            if ip == "Inconnue":
                continue

            # Simulation d'un parsing d'heure (année courante fictive 2026)
            try:
                dt = datetime.strptime(f"2026 {entree['timestamp_str']}", "%Y %b %d %H:%M:%S")
            except ValueError:
                continue

            if ip not in tentatives_echec:
                tentatives_echec[ip] = []
            tentatives_echec[ip].append({"dt": dt, "entree": entree})

    alertes_bruteforce = []

    for ip, echecs in tentatives_echec.items():
        echecs.sort(key=lambda x: x["dt"])
        # Fenêtre glissante
        i = 0
        while i < len(echecs):
            fenetre_debut = echecs[i]["dt"]
            fenetre_fin = fenetre_debut + timedelta(minutes=fenetre_minutes)

            # Regrouper tous les échecs dans cette fenêtre
            groupe = [e for e in echecs if fenetre_debut <= e["dt"] <= fenetre_fin]

            if len(groupe) >= seuil:
                alertes_bruteforce.append({
                    "ip_source": ip,
                    "nombre_tentatives": len(groupe),
                    "premiere_tentative": groupe[0]["entree"]["timestamp_str"],
                    "derniere_tentative": groupe[-1]["entree"]["timestamp_str"],
                    "preuves": [g["entree"]["ligne_brute"] for g in groupe]
                })
                break  # Une alerte par IP suffit pour ce rapport
            i += 1

    return alertes_bruteforce

def extraire_iocs(entrees: List[Dict[str, Any]]) -> Dict[str, list]:
    """
    Extrait les Indicateurs de Compromission (IOCs) : IPs, comptes ciblés.
    """
    ips = set()
    comptes = set()

    for entree in entrees:
        msg = entree["message"]
        if entree["ip_source"] != "Inconnue":
            ips.add(entree["ip_source"])

        # Recherche de noms d'utilisateurs ciblés
        user_match = re.search(r'for (?:invalid user )?([^\s]+) from', msg)
        if user_match:
            comptes.add(user_match.group(1))

    return {
        "ips_uniques": list(ips),
        "comptes_cibles": list(comptes)
    }
