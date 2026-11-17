import os
import numpy as np
from google import genai
from google.genai import types
from dotenv import load_dotenv

load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

class BaseConnaissancesRAG:
    def __init__(self, chemin_doc: str = "docs/politique_securite.md"):
        self.morceaux = []
        self.embeddings = []
        self._charger_et_vectoriser(chemin_doc)

    def _charger_et_vectoriser(self, chemin: str):
        if not os.path.exists(chemin):
            # Fallback si le doc n'est pas encore créé
            self.morceaux = ["Politique de sécurité par défaut : Brute-force >= 5 échecs = Moyenne/Élevée. Escalade N2 si succès."]
        else:
            with open(chemin, "r", encoding="utf-8") as f:
                contenu = f.read()
            # Découpage simple par paragraphes ou sections
            self.morceaux = [p.strip() for p in contenu.split("\n\n") if p.strip()]

        # Génération des embeddings via le modèle gratuit gemini-embedding-001
        for texte in self.morceaux:
            response = client.models.embed_content(
                model="gemini-embedding-001",
                contents=texte
            )
            # Extraction du vecteur numérique
            vecteur = response.embeddings[0].values
            self.embeddings.append(np.array(vecteur))

    def rechercher(self, requete: str, top_k: int = 2) -> list:
        """
        Recherche les extraits les plus pertinents par similarité cosinus.
        """
        if not self.morceaux:
            return []

        # Embedding de la requête
        resp_req = client.models.embed_content(
            model="gemini-embedding-001",
            contents=requete
        )
        vec_req = np.array(resp_req.embeddings[0].values)

        similarites = []
        for i, vec_doc in enumerate(self.embeddings):
            # Calcul de la similarité cosinus
            produit_scalaire = np.dot(vec_req, vec_doc)
            norme_a = np.linalg.norm(vec_req)
            norme_b = np.linalg.norm(vec_doc)

            if norme_a == 0 or norme_b == 0:
                sim = 0.0
            else:
                sim = produit_scalaire / (norme_a * norme_b)
            similarites.append((sim, self.morceaux[i]))

        # Tri par similarité décroissante
        similarites.sort(key=lambda x: x[0], reverse=True)
        return [item[1] for item in similarites[:top_k]]

# Instance globale pour le projet
rag_system = BaseConnaissancesRAG()

def rechercher_base_connaissances(requete: str) -> str:
    resultats = rag_system.rechercher(requete)
    return "\n---\n".join(resultats)
