# Carrefour AI Assistant - Backend API

Ce dossier contient le "cerveau" de l'assistant, exposé via une API **FastAPI**. Il utilise **LangGraph** pour orchestrer une logique agentique capable d'analyser le contexte de navigation en temps réel.

## Architecture Agentique (LangGraph)

L'agent ne suit pas un script linéaire simple. Il est modélisé sous forme de graphe d'états (`app/agent/graph.py`) qui gère intelligemment deux modes de fonctionnement :

1.  **Mode Proactif (Smart Pre-prompts)** :
    *   **Déclencheur** : L'utilisateur navigue sur une page (Home, Search, Product) sans envoyer de message.
    *   **Action** : L'agent analyse le DOM (produits visibles, promos) et génère des suggestions de questions pertinentes (ex: "Quel est le prix au kilo ?").
    *   **Sortie** : Liste de `suggestions`.

2.  **Mode Réactif (Chatbot)** :
    *   **Déclencheur** : L'utilisateur pose une question.
    *   **Action** : L'agent utilise le contexte de la page et l'historique pour répondre.
    *   **Sortie** : Une réponse textuelle (`final_response`).

## 🛠 Stack Technique

*   **Framework** : FastAPI (Python 3.9+)
*   **LLM** : Google Vertex AI (Gemini 1.5 Pro)
*   **Orchestration** : LangGraph & LangChain
*   **Observabilité** : Langfuse (Tracing complet des requêtes et coûts)
*   **Validation** : Pydantic

## 📂 Structure du Dossier

```text
backend/
├── app/
│   ├── agent/
│   │   ├── graph.py       # Définition du StateGraph (Noeuds & Logique conditionnelle)
│   │   └── __init__.py
│   ├── tools/             # Outils (ex: Recherche simulée)
│   ├── config.py          # Gestion centralisée de la config (Env vars)
│   ├── main.py            # Point d'entrée API & Middleware CORS
│   └── schemas.py         # Modèles de données partagés (Frontend <-> Backend)
├── requirements.txt       # Dépendances
└── .env                   # Variables d'environnement (non versionné)
```

## 🚀 Installation & Démarrage

### 1. Configuration
Créez un fichier `.env` à la racine de `backend/` :

```ini
GOOGLE_APPLICATION_CREDENTIALS="path/to/your-gcp-key.json"
GCP_PROJECT_ID="votre-projet-id"
GCP_LOCATION="europe-west1"

LANGFUSE_PUBLIC_KEY="pk-lf-..."
LANGFUSE_SECRET_KEY="sk-lf-..."
LANGFUSE_HOST="https://cloud.langfuse.com"
```

### 2. Installation des dépendances

```bash
python -m venv venv
source venv/bin/activate  # ou venv\Scripts\activate sur Windows
pip install -r requirements.txt
```

### 3. Lancer le serveur

```bash
uvicorn app.main:app --reload
```

L'API sera accessible sur `http://localhost:8000`.
La documentation interactive (Swagger UI) est disponible sur `http://localhost:8000/docs`.