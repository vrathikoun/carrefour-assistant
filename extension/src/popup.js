document.addEventListener("DOMContentLoaded", async () => {
  const data = await chrome.storage.local.get("latest_context");
  const context = data.latest_context;

  if (!context) {
    addMessage("bot", "Veuillez naviguer sur Carrefour.fr pour activer l'assistant.");
    return;
  }

  // 1) Suggestions proactives (appel /suggestions)
  requestSuggestions(context);

  // 2) Send message
  document.getElementById("send-btn").addEventListener("click", async () => {
    const input = document.getElementById("user-input");
    const text = input.value.trim();
    if (!text) return;

    addMessage("user", text);
    input.value = "";
    await callChat(text, context);
  });
});

async function requestSuggestions(context) {
  const suggestionsArea = document.getElementById("suggestions-area");
  suggestionsArea.innerHTML = "Chargement...";

  chrome.runtime.sendMessage(
    { type: "API_SUGGESTIONS", payload: { context } },
    (resp) => {
      if (!resp?.ok) {
        suggestionsArea.innerHTML = "Erreur suggestions.";
        return;
      }
      renderSuggestions(resp.data?.suggestions || [], context);
    }
  );
}

async function callChat(message, context) {
  const suggestionsArea = document.getElementById("suggestions-area");
  suggestionsArea.innerHTML = "Chargement...";

  chrome.runtime.sendMessage(
    { type: "API_CHAT", payload: { message, context } },
    (resp) => {
      if (!resp?.ok) {
        addMessage("bot", "Erreur de connexion au backend.");
        console.error(resp?.error);
        suggestionsArea.innerHTML = "";
        return;
      }

      const json = resp.data || {};
      if (json.response) addMessage("bot", json.response);

      // refresh suggestions if backend returns some
      if (json.suggestions?.length) {
        renderSuggestions(json.suggestions, context);
      } else {
        suggestionsArea.innerHTML = "";
      }
    }
  );
}

function renderSuggestions(suggestions, context) {
  const suggestionsArea = document.getElementById("suggestions-area");
  suggestionsArea.innerHTML = "";
  suggestions.slice(0, 3).forEach((s) => {
    const btn = document.createElement("div");
    btn.className = "suggestion";
    btn.innerText = s;
    btn.onclick = async () => {
      addMessage("user", s);
      await callChat(s, context);
    };
    suggestionsArea.appendChild(btn);
  });
}

function addMessage(role, text) {
  const div = document.createElement("div");
  div.className = `msg ${role}`;
  div.innerText = text;
  document.getElementById("chat-history").appendChild(div);
}