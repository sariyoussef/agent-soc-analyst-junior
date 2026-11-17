# SOC Analyst Junior — AI Agent powered by Google Gemini

**Language / Langue :** [English](#english) · [Français](#français)

![Python](https://img.shields.io/badge/python-3.11%2B-blue) ![Gemini API](https://img.shields.io/badge/powered%20by-Gemini%20API-8E75B2) ![MCP](https://img.shields.io/badge/bonus-MCP-orange) ![License](https://img.shields.io/badge/license-MIT-green)

<!-- Optional: add a screenshot or GIF of the agent in action here / Optionnel : ajoutez ici une capture d'écran ou un GIF de l'agent en action -->

---

## English

### Project overview

**SOC Analyst Junior** is an AI agent built for educational purposes that reproduces the daily work of a junior SOC (Security Operations Center) analyst. Given a raw Linux authentication log (`auth.log`), the agent:

1. **Analyzes** the log file and extracts authentication events (SSH successes and failures).
2. **Detects anomalies** — brute-force attempts are flagged when at least **5 failed SSH logins** occur from the same IP address within **10 minutes**.
3. **Produces deliverables**: a structured incident report (severity, MITRE ATT&CK category, IOCs, log evidence) and an alert email in French for the network team.

It was designed as a course project to demonstrate the main building blocks of a modern LLM agent: system instructions, skills, tools (function calling), connectors, plugins, MCP, a knowledge base (RAG), short/long-term memory and secure authentication.

### The 9 implemented features

| # | Required feature | Where it is implemented | Why it matters |
|---|---|---|---|
| 1 | **Instructions (System Prompt)** | `system_prompt.py` (`SYSTEM_PROMPT`) | Defines the agent's identity (junior analyst under supervision), its rules (never invent facts, always quote log lines as evidence) and the imposed output formats. |
| 2 | **Skills** | Listed inside the system prompt | Explicit capabilities: log analysis, IOC extraction, severity classification, incident escalation to a level-2 analyst. |
| 3 | **Tools** | `outils_agent.py` (function calling schemas) + `log_analyse.py` | Executable functions the model can call: `analyser_authlog`, `detecter_bruteforce`, `generer_rapport`, `envoyer_alerte`, etc. |
| 4 | **Connectors** | `connecteurs.py` | External services: Discord/Slack webhook alert + SMTP email sending (with a simulated fallback mode when no credentials are available). |
| 5 | **Plugins** | Google Search grounding | Pre-built capability added to the model to enrich analysis with public context on suspicious IPs. |
| 6 | **MCP (bonus)** | `serveur_mcp.py` | Model Context Protocol server (official SDK, stdio transport) exposing 3 agent tools, connected to Gemini CLI via a `mcpServers` configuration — standardized and secure access. |
| 7 | **Knowledge Base (RAG)** | `base_connaissances.py` | Minimal RAG pipeline on the internal security policy (`docs/politique_securite.md`): chunking + embeddings (`gemini-embedding-001`) + cosine similarity search, with no paid vector database. |
| 8 | **Memory** | `memoire.py` | Short-term: conversation history managed by the code. Long-term: incidents and user preferences persisted in `incidents.json`. |
| 9 | **Authentication** | `.env` + `python-dotenv` | The Gemini API key is stored in an environment variable, never hardcoded; `.gitignore` prevents any secret from being committed. |

### Project structure

```text
.
├── agent_soc.py            # Main agent loop (Gemini API + function calling)
├── outils_agent.py         # Tool declarations (JSON schemas)
├── log_analyse.py          # auth.log parser + brute-force detection + IOC extraction
├── base_connaissances.py   # Minimal RAG (chunking, embeddings, cosine similarity)
├── memoire.py              # Short-term (history) and long-term (JSON) memory
├── connecteurs.py          # Webhook (Discord/Slack) + SMTP email connectors
├── serveur_mcp.py          # MCP server exposing the agent tools (bonus)
├── system_prompt.py        # System instructions of the agent
├── .env.example            # Template of the required environment variables
├── .gitignore              # Prevents secrets and runtime files from being committed
├── docs/
│   └── politique_securite.md   # Internal security policy (knowledge base source)
└── exemples/
    └── auth.log            # Realistic sample log (contains a brute-force attempt)
```

### Installation

**Prerequisites:** Python 3.11+ and a free Gemini API key (create one on [Google AI Studio](https://aistudio.google.com)).

```bash
# 1. Install the dependencies
pip install google-genai python-dotenv mcp numpy

# 2. Create your local configuration (never commit this file)
#    Linux / macOS:
cp .env.example .env
#    Windows:
copy .env.example .env
```

Then open `.env` and fill in your key:

```text
GEMINI_API_KEY=your_api_key_here
```

### Usage

```bash
python agent_soc.py
```

Then chat with the agent in natural language (French works best, English is supported). Example session:

```text
> Analyse le fichier exemples/auth.log et détecte les activités suspectes.
[tool call] analyser_authlog("exemples/auth.log")
[tool call] detecter_bruteforce(...)
> Rapport généré : rapports/rapport_INC-2026-001.md
```

### Test missions

Three reproducible missions demonstrate the agent end to end:

| Mission | Prompt sent to the agent | Features demonstrated |
|---|---|---|
| 1 | "Analyse le fichier exemples/auth.log et identifie les 3 adresses IP les plus suspectes." | Tools, brute-force detection, evidence quoting |
| 2 | "Rédige un e-mail d'alerte en français pour l'équipe réseau au sujet de l'incident de brute-force détecté." | Connectors, report writing, French output |
| 3 | "Que dit notre politique de sécurité interne sur les tentatives de brute-force et que dois-je faire ?" | Knowledge base (RAG), long-term memory |

### MCP bonus — connect Gemini CLI to the agent tools

The file `serveur_mcp.py` exposes three tools through the Model Context Protocol. To use them from Gemini CLI (free), add this to your Gemini CLI settings (`settings.json`):

```json
{
  "mcpServers": {
    "soc-tools": {
      "command": "python",
      "args": ["serveur_mcp.py"]
    }
  }
}
```

### Security notes

- The API key lives only in `.env`, which is excluded from version control by `.gitignore`.
- The agent never performs destructive actions: blocking an IP is always a **recommendation**, never an action.
- The agent escalates to a level-2 analyst when severity is critical or information is insufficient.

### Disclaimer

This is an educational project. The sample log uses the documentation IP range `203.0.113.0/24` (TEST-NET-3) and contains no real data. Do not point this agent at production logs without proper authorization.

### License

Released under the MIT License.

---

## Français

### Aperçu du projet

**SOC Analyst Junior** est un agent IA à but pédagogique qui reproduit le travail quotidien d'un analyste junior d'un SOC (Security Operations Center). À partir d'un journal d'authentification Linux brut (`auth.log`), l'agent :

1. **Analyse** le fichier de log et extrait les événements d'authentification (connexions SSH réussies et échouées).
2. **Détecte les anomalies** — une tentative de brute-force est signalée lorsqu'au moins **5 échecs SSH** proviennent de la même adresse IP en moins de **10 minutes**.
3. **Produit les livrables** : un rapport d'incident structuré (sévérité, catégorie MITRE ATT&CK, IOCs, preuves issues des logs) et un e-mail d'alerte en français pour l'équipe réseau.

Ce projet a été conçu dans un cadre de cours pour démontrer les principaux composants d'un agent LLM moderne : instructions système, compétences, outils (function calling), connecteurs, plugins, MCP, base de connaissances (RAG), mémoire court/long terme et authentification sécurisée.

### Les 9 fonctionnalités implémentées

| # | Fonctionnalité exigée | Où elle est implémentée | Pourquoi c'est important |
|---|---|---|---|
| 1 | **Instructions (System Prompt)** | `system_prompt.py` (`SYSTEM_PROMPT`) | Définit l'identité de l'agent (analyste junior sous supervision), ses règles (ne jamais inventer, toujours citer les lignes de log comme preuves) et les formats de sortie imposés. |
| 2 | **Compétences (Skills)** | Listées dans le system prompt | Capacités explicites : analyse de logs, extraction d'IOCs, classification de sévérité, escalade vers un analyste niveau 2. |
| 3 | **Outils (Tools)** | `outils_agent.py` (schémas function calling) + `log_analyse.py` | Fonctions exécutables par le modèle : `analyser_authlog`, `detecter_bruteforce`, `generer_rapport`, `envoyer_alerte`, etc. |
| 4 | **Connecteurs** | `connecteurs.py` | Services externes : alerte via webhook Discord/Slack + envoi d'e-mail SMTP (avec un mode simulé si aucun identifiant n'est disponible). |
| 5 | **Plugins** | Google Search grounding | Capacité préconçue ajoutée au modèle pour enrichir l'analyse avec un contexte public sur les IP suspectes. |
| 6 | **MCP (bonus)** | `serveur_mcp.py` | Serveur MCP (SDK officiel, transport stdio) exposant 3 outils de l'agent, connecté à Gemini CLI via une configuration `mcpServers` — accès standardisé et sécurisé. |
| 7 | **Base de connaissances (RAG)** | `base_connaissances.py` | Pipeline RAG minimal sur la politique de sécurité interne (`docs/politique_securite.md`) : découpage + embeddings (`gemini-embedding-001`) + recherche par similarité cosinus, sans base vectorielle payante. |
| 8 | **Mémoire** | `memoire.py` | Court terme : historique de conversation géré par le code. Long terme : incidents et préférences persistés dans `incidents.json`. |
| 9 | **Authentification** | `.env` + `python-dotenv` | La clé API Gemini est stockée dans une variable d'environnement, jamais en dur dans le code ; `.gitignore` empêche tout secret d'être versionné. |

### Structure du projet

```text
.
├── agent_soc.py            # Boucle principale de l'agent (API Gemini + function calling)
├── outils_agent.py         # Déclarations des tools (schémas JSON)
├── log_analyse.py          # Parseur auth.log + détection brute-force + extraction d'IOCs
├── base_connaissances.py   # RAG minimal (découpage, embeddings, similarité cosinus)
├── memoire.py              # Mémoire court terme (historique) et long terme (JSON)
├── connecteurs.py          # Connecteurs webhook (Discord/Slack) + e-mail SMTP
├── serveur_mcp.py          # Serveur MCP exposant les outils de l'agent (bonus)
├── system_prompt.py        # Instructions système de l'agent
├── .env.example            # Modèle des variables d'environnement requises
├── .gitignore              # Empêche les secrets et fichiers d'exécution d'être versionnés
├── docs/
│   └── politique_securite.md   # Politique de sécurité interne (source de la base de connaissances)
└── exemples/
    └── auth.log            # Log d'exemple réaliste (contient une tentative de brute-force)
```

### Installation

**Prérequis :** Python 3.11+ et une clé API Gemini gratuite (à créer sur [Google AI Studio](https://aistudio.google.com)).

```bash
# 1. Installer les dépendances
pip install google-genai python-dotenv mcp numpy

# 2. Créer la configuration locale (ne jamais versionner ce fichier)
#    Linux / macOS :
cp .env.example .env
#    Windows :
copy .env.example .env
```

Ouvrez ensuite `.env` et renseignez votre clé :

```text
GEMINI_API_KEY=votre_cle_ici
```

### Utilisation

```bash
python agent_soc.py
```

Discutez ensuite avec l'agent en langage naturel (le français fonctionne le mieux, l'anglais est aussi accepté). Exemple de session :

```text
> Analyse le fichier exemples/auth.log et détecte les activités suspectes.
[appel d'outil] analyser_authlog("exemples/auth.log")
[appel d'outil] detecter_bruteforce(...)
> Rapport généré : rapports/rapport_INC-2026-001.md
```

### Missions de test

Trois missions reproductibles démontrent l'agent de bout en bout :

| Mission | Prompt envoyé à l'agent | Fonctionnalités démontrées |
|---|---|---|
| 1 | « Analyse le fichier exemples/auth.log et identifie les 3 adresses IP les plus suspectes. » | Outils, détection de brute-force, citation des preuves |
| 2 | « Rédige un e-mail d'alerte en français pour l'équipe réseau au sujet de l'incident de brute-force détecté. » | Connecteurs, rédaction de rapport, sortie en français |
| 3 | « Que dit notre politique de sécurité interne sur les tentatives de brute-force et que dois-je faire ? » | Base de connaissances (RAG), mémoire long terme |

### Bonus MCP — connecter Gemini CLI aux outils de l'agent

Le fichier `serveur_mcp.py` expose trois outils via le Model Context Protocol. Pour les utiliser depuis Gemini CLI (gratuit), ajoutez ceci aux paramètres de Gemini CLI (`settings.json`) :

```json
{
  "mcpServers": {
    "soc-tools": {
      "command": "python",
      "args": ["serveur_mcp.py"]
    }
  }
}
```

### Notes de sécurité

- La clé API ne se trouve que dans `.env`, exclu du versionnement par `.gitignore`.
- L'agent n'exécute jamais d'action destructive : le blocage d'une IP est toujours une **recommandation**, jamais une action.
- L'agent escalade vers un analyste niveau 2 lorsque la sévérité est critique ou que l'information est insuffisante.

### Avertissement

Projet à but éducatif. Le log d'exemple utilise la plage d'IP de documentation `203.0.113.0/24` (TEST-NET-3) et ne contient aucune donnée réelle. Ne pointez pas cet agent vers des logs de production sans autorisation appropriée.

### Licence

Projet publié sous licence MIT.
