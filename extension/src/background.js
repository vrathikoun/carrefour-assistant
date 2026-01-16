// Écoute les messages venant du content script (la page web)
chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  if (message.type === "PAGE_CONTEXT") {
    console.log("Context received:", message.payload);
    // Sauvegarde dans le storage local du navigateur
    chrome.storage.local.set({ latest_context: message.payload });
  }
});