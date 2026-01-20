const DEFAULT_BACKEND_BASE = "https://8000-viphone-vm1.cluster-t346zipbh5hmsxvtfeq3qnclfy.cloudworkstations.dev/"; 

async function getBackendBase() {
  const { backendBase } = await chrome.storage.local.get(["backendBase"]);
  return backendBase || DEFAULT_BACKEND_BASE;
}

chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  (async () => {
    try {
      // stock context
      if (message.type === "PAGE_CONTEXT") {
        await chrome.storage.local.set({ latest_context: message.payload });
        sendResponse({ ok: true });
        return;
      }

      const base = await getBackendBase();

      if (message.type === "API_CHAT") {
        const res = await fetch(`${base}/chat`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            message: message.payload.message,
            context: message.payload.context,
            chat_history: message.payload.chat_history || []
          })
        });
        const data = await res.json();
        sendResponse({ ok: true, data });
        return;
      }

      if (message.type === "API_SUGGESTIONS") {
        const res = await fetch(`${base}/suggestions`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ context: message.payload.context })
        });
        const data = await res.json();
        sendResponse({ ok: true, data });
        return;
      }

      sendResponse({ ok: false, error: "Unknown message type" });
    } catch (e) {
      sendResponse({ ok: false, error: String(e) });
    }
  })();

  return true; // async
});