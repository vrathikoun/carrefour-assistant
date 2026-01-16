const API_URL = "http://localhost:8000/chat";

document.addEventListener("DOMContentLoaded", async () => {
  // 1. Récupérer le contexte stocké par background.js
  const data = await chrome.storage.local.get("latest_context");
  const context = data.latest_context;

  if (!context) {
    addMessage("bot", "Veuillez naviguer sur Carrefour.fr pour activer l'assistant.");
    return;
  }

  // 2. Appel initial pour les "Smart Pre-prompts" (sans message utilisateur)
  // L'agent va détecter qu'il n'y a pas de message et lancer l'analyse proactive
  callAgent("", context);

  // 3. Gestion du bouton envoyer
  document.getElementById("send-btn").addEventListener("click", () => {
    const input = document.getElementById("user-input");
    const text = input.value.trim();
    if (text) {
      addMessage("user", text);
      callAgent(text, context);
      input.value = "";
    }
  });
});

async function callAgent(message, context) {
  const suggestionsArea = document.getElementById("suggestions-area");
  suggestionsArea.innerHTML = "Chargement...";

  try {
    const response = await fetch(API_URL, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message, context })
    });
    const json = await response.json();

    if (json.response) {
      addMessage("bot", json.response);
    }

    // Affichage des suggestions (Smart Pre-prompts)
    suggestionsArea.innerHTML = "";
    if (json.suggestions && json.suggestions.length > 0) {
      json.suggestions.forEach(s => {
        const btn = document.createElement("div");
        btn.className = "suggestion";
        btn.innerText = s;
        btn.onclick = () => {
            addMessage("user", s);
            callAgent(s, context);
        };
        suggestionsArea.appendChild(btn);
      });
    }
  } catch (e) {
    addMessage("bot", "Erreur de connexion au backend.");
    console.error(e);
  }
}

function addMessage(role, text) {
  const div = document.createElement("div");
  div.className = `msg ${role}`;
  div.innerText = text;
  document.getElementById("chat-history").appendChild(div);
}