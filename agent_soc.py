import os
import time
from google import genai
from google.genai import types
from google.genai.errors import ServerError
from dotenv import load_dotenv
from outils_agent import executer_outil

load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

# Déclaration des outils (Function declarations) pour le SDK google-genai
declarations_outils = [
    types.Tool(function_declarations=[
        types.FunctionDeclaration(
            name="detecter_bruteforce",
            description="Analyse un fichier auth.log pour détecter les attaques par force brute SSH.",
            parameters=types.Schema(
                type=types.Type.OBJECT,
                properties={"chemin_fichier": types.Schema(type=types.Type.STRING, description="Chemin vers le log")},
            ),
        ),
        types.FunctionDeclaration(
            name="rechercher_base_connaissances",
            description="Interroge la politique de sécurité interne sur les consignes et la sévérité.",
            parameters=types.Schema(
                type=types.Type.OBJECT,
                properties={"requete": types.Schema(type=types.Type.STRING, description="Question sur la politique")},
            ),
        ),
        types.FunctionDeclaration(
            name="envoyer_alerte",
            description="Envoie un e-mail d'alerte et un message webhook à l'équipe réseau.",
            parameters=types.Schema(
                type=types.Type.OBJECT,
                properties={
                    "destinataire": types.Schema(type=types.Type.STRING, description="E-mail du destinataire"),
                    "sujet": types.Schema(type=types.Type.STRING, description="Objet de l'alerte"),
                    "corps": types.Schema(type=types.Type.STRING, description="Contenu textuel de l'alerte en français")
                },
                required=["sujet", "corps"]
            ),
        ),
        types.FunctionDeclaration(
            name="consulter_memoire",
            description="Consulte l'historique des incidents passés mémorisés.",
            parameters=types.Schema(type=types.Type.OBJECT, properties={})
        )
    ])
]

system_instruction = """
Tu es "SOC Analyst Junior", un agent virtuel de niveau analyste junior en cybersécurité.
Tu analyses les logs auth.log, détectes les anomalies (brute-force), extrais les IOCs,
consultes la base de connaissances (politique de sécurité) et rédiges des rapports ou alertes.
Cite toujours les preuves textuelles exactes. Ne jamais inventer d'informations.
"""

def appeler_gemini_avec_retry(contents, config, max_essais: int = 4):
    """Appelle l'API Gemini en gérant automatiquement les erreurs temporaires 503."""
    modeles = ["gemini-3.5-flash-lite", "gemini-3.8-flash", "gemini-3.5-flash-lite"]
    for essai in range(max_essais):
        modele_actuel = modeles[essai % len(modeles)]
        try:
            return client.models.generate_content(
                model=modele_actuel,
                contents=contents,
                config=config
            )
        except ServerError as e:
            if "503" in str(e) and essai < max_essais - 1:
                attente = (essai + 1) * 3
                print(f"[INFO API] Serveur occupé (503) sur {modele_actuel}. Nouvelle tentative dans {attente}s...")
                time.sleep(attente)
            else:
                raise

def executer_requete_agent(prompt_utilisateur: str):
    """
    Gère la conversation avec la boucle d'exécution des outils (Function Calling).
    """
    config = types.GenerateContentConfig(
        system_instruction=system_instruction,
        tools=declarations_outils,
        temperature=0.2,
    )

    print(f"\n[UTILISATEUR] : {prompt_utilisateur}")

    historique = [
        types.Content(role="user", parts=[types.Part.from_text(text=prompt_utilisateur)])
    ]

    response = appeler_gemini_avec_retry(historique, config)

    while response.function_calls:
        historique.append(response.candidates[0].content)

        parts_reponses = []
        for function_call in response.function_calls:
            nom_fonction = function_call.name
            args = dict(function_call.args)
            print(f"[AGENT - APPEL OUTIL] Exécution de '{nom_fonction}' avec les arguments {args}...")

            resultat_fonction = executer_outil(nom_fonction, args)
            print(f"[RÉSULTAT OUTIL] : {str(resultat_fonction)[:150]}...")

            parts_reponses.append(
                types.Part.from_function_response(
                    name=nom_fonction,
                    response={"result": resultat_fonction}
                )
            )

        historique.append(types.Content(role="user", parts=parts_reponses))
        response = appeler_gemini_avec_retry(historique, config)

    print(f"\n[AGENT - RÉPONSE FINALE] :\n{response.text}")
    return response.text

if __name__ == "__main__":
    print("=== Agent SOC Analyst Junior prêt (tapez 'quitter' ou 'exit' pour arrêter) ===")
    while True:
        try:
            prompt = input("\n[VOUS] > ").strip()
            if not prompt:
                continue
            if prompt.lower() in ["quitter", "exit", "quit"]:
                print("Fermeture de l'agent SOC.")
                break

            executer_requete_agent(prompt)
        except KeyboardInterrupt:
            print("\nInterruption détectée. Fermeture de l'agent SOC.")
            break
