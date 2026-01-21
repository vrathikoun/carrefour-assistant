// extension/src/background.js

// --- MV3 Service Worker: store context + call backend API (avoid CORS from popup) ---
const API_BASE = "https://carrefour-assistant-api-62829646645.europe-west1.run.app";

// Small helper: fetch with timeout
async function fetchWithTimeout(url, options = {}, timeoutMs = 15000) {
  const controller = new AbortController();
  const id = setTimeout(() => controller.abort(), timeoutMs);

  try {
    const res = await fetch(url, { ...options, signal: controller.signal });
    return res;
  } finally {
    clearTimeout(id);
  }
}

async function apiPost(path, body) {
  const url = `${API_BASE}${path}`;
  const res = await fetchWithTimeout(url, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });

  const text = await res.text();
  let data = null;

  try {
    data = text ? JSON.parse(text) : null;
  } catch (e) {
    // keep raw if non-json
    data = { raw: text };
  }

  if (!res.ok) {
    const errMsg = data?.detail || data?.raw || `${res.status} ${res.statusText}`;
    throw new Error(errMsg);
  }

  return data;
}

// Store latest context received from content script
chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  // 1) Context ingestion
  if (message?.type === "PAGE_CONTEXT") {
    console.log("[bg] PAGE_CONTEXT received:", message.payload);
    chrome.storage.local.set({ latest_context: message.payload });
    sendResponse({ ok: true });
    return; // sync response ok
  }

  // 2) API suggestions call
  if (message?.type === "API_SUGGESTIONS") {
    (async () => {
      try {
        const { context } = message.payload || {};
        if (!context) throw new Error("Missing context in API_SUGGESTIONS");

        const data = await apiPost("/suggestions", { context });
        sendResponse({ ok: true, data });
      } catch (err) {
        console.error("[bg] API_SUGGESTIONS error:", err);
        sendResponse({ ok: false, error: String(err?.message || err) });
      }
    })();
    return true; // keep channel open for async sendResponse
  }

  // 3) API chat call
  if (message?.type === "API_CHAT") {
    (async () => {
      try {
        const { message: userMessage, context } = message.payload || {};
        if (!context) throw new Error("Missing context in API_CHAT");

        const data = await apiPost("/chat", { message: userMessage, context });
        sendResponse({ ok: true, data });
      } catch (err) {
        console.error("[bg] API_CHAT error:", err);
        sendResponse({ ok: false, error: String(err?.message || err) });
      }
    })();
    return true; // keep channel open
  }

  // default
  sendResponse({ ok: false, error: "Unknown message type" });
});
