import json
import os
from typing import List, Dict, Any

FICHIER_INCIDENTS = "incidents.json"

class MemoireLongTerme:
    def __init__(self, fichier: str = FICHIER_INCIDENTS):
        self.fichier = fichier
        self._initialiser()

    def _initialiser(self):
        if not os.path.exists(self.fichier):
            self.sauvegarder({
                "preferences": {"niveau_alerte_defaut": "Moyenne", "langue": "français"},
                "incidents_passes": []
            })

    def charger(self) -> Dict[str, Any]:
        """Charge la mémoire long terme depuis le fichier JSON."""
        try:
            with open(self.fichier, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {"preferences": {}, "incidents_passes": []}

    def sauvegarder(self, data: Dict[str, Any]):
        with open(self.fichier, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)

    def enregistrer_incident(self, rapport: Dict[str, Any]):
        data = self.charger()
        data["incidents_passes"].append(rapport)
        self.sauvegarder(data)

# Instance globale
memoire_lt = MemoireLongTerme()

def consulter_memoire() -> str:
    """Consulte l'historique des incidents résolus et mémorisés."""
    data = memoire_lt.charger()
    return json.dumps(data, ensure_ascii=False, indent=2)
