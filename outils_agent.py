from log_analyse import analyser_authlog, detecter_bruteforce, extraire_iocs
from base_connaissances import rechercher_base_connaissances
from memoire import consulter_memoire, memoire_lt
from connecteurs import envoyer_alerte_discord, envoyer_email
import json

# Définition des fonctions exécutables mappées pour l'agent
def executer_outil(nom_outil: str, args: dict) -> str:
    if nom_outil == "analyser_authlog":
        chemin = args.get("chemin_fichier", "exemples/auth.log")
        resultats = analyser_authlog(chemin)
        # Renvoyer un résumé pour éviter de saturer le contexte
        iocs = extraire_iocs(resultats)
        return json.dumps({"total_lignes": len(resultats), "iocs": iocs}, ensure_ascii=False)

    elif nom_outil == "detecter_bruteforce":
        chemin = args.get("chemin_fichier", "exemples/auth.log")
        entrees = analyser_authlog(chemin)
        alertes = detecter_bruteforce(entrees)
        return json.dumps(alertes, ensure_ascii=False)

    elif nom_outil == "rechercher_base_connaissances":
        requete = args.get("requete", "")
        return rechercher_base_connaissances(requete)

    elif nom_outil == "generer_rapport":
        rapport = args.get("rapport_dict", {})
        memoire_lt.enregistrer_incident(rapport)
        # Sauvegarde d'une copie markdown locale
        with open("dernier_rapport.md", "w", encoding="utf-8") as f:
            f.write(f"# RAPPORT D'INCIDENT SOC\n\n```json\n{json.dumps(rapport, indent=2, ensure_ascii=False)}\n```")
        return "Rapport généré, enregistré dans la mémoire long terme et exporté dans dernier_rapport.md."

    elif nom_outil == "envoyer_alerte":
        destinataire = args.get("destinataire", "reseau-secours@example.com")
        sujet = args.get("sujet", "Alerte de Sécurité SOC")
        corps = args.get("corps", "")
        res_email = envoyer_email(destinataire, sujet, corps)
        res_disc = envoyer_alerte_discord(corps)
        return f"{res_email} | {res_disc}"

    elif nom_outil == "consulter_memoire":
        return consulter_memoire()

    return f"Erreur : Outil {nom_outil} inconnu."
