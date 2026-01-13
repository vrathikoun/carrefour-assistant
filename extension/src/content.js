function detectPageType() {
  const url = location.href;
  if (url === "https://www.carrefour.fr/" || url === "https://www.carrefour.fr") return "HOME";
  if (url.includes("/s?") || url.includes("/recherche")) return "SEARCH";
  if (url.includes("/p/")) return "PRODUCT";
  return "OTHER";
}

function getText(el) {
  return (el?.innerText || "").replace(/\s+/g, " ").trim();
}

function extractSearchProducts() {
  // Generic fallback: card retrieval and title/price extraction
  const cards = Array.from(document.querySelectorAll("article, li, div[class*='product'], div[class*='item']"))
    .filter(n => n.querySelector && (n.querySelector("[class*=price]") || n.querySelector("a")))
    .slice(0, 15);

  const products = [];
  for (const c of cards) {
    const title = getText(c.querySelector("h2, h3, [class*=title], a"));
    const price = getText(c.querySelector("[class*=price], [data-testid*=price]"));
    if (title && price) products.push({ title, price });
  }
  return products.slice(0, 10);
}

function extractHomePromos() {
  // Heuristics: identifying sections with keywords like "promo", "offer", "discount"
  const nodes = Array.from(document.querySelectorAll("section, article, div"))
    .filter(n => /promo|offre|réduction|%/i.test(getText(n)))
    .slice(0, 8);

  return nodes.map(n => getText(n)).filter(t => t.length > 20).slice(0, 5);
}

function extractProduct() {
  const title = getText(document.querySelector("h1"));
  const price = getText(document.querySelector("[class*=price], [data-testid*=price]"));
  const desc = getText(document.querySelector("[class*=description], main"));
  return { title, price, desc: desc.slice(0, 1200) };
}

function extractContext() {
  const page_type = detectPageType();
  const base = {
    url: location.href,
    title: document.title,
    page_type
  };

  if (page_type === "HOME") return { ...base, promos: extractHomePromos() };
  if (page_type === "SEARCH") return { ...base, products: extractSearchProducts() };
  if (page_type === "PRODUCT") return { ...base, product: extractProduct() };

  // fallback: page text 
  const bodyText = getText(document.body).slice(0, 3000);
  return { ...base, bodyText };
}

// Debounce utility to avoid spamming the extension bus during page load/scroll
function debounce(func, wait) {
  let timeout;
  return function(...args) {
    clearTimeout(timeout);
    timeout = setTimeout(() => func.apply(this, args), wait);
  };
}

// Main execution logic wrapped in debounce
const runExtraction = debounce(() => {
  chrome.runtime.sendMessage({ type: "PAGE_CONTEXT", payload: extractContext() });
}, 1000);

// 1. Run initially
runExtraction();

// 2. Observe DOM changes (SPA navigation & Lazy loading)
const observer = new MutationObserver(() => runExtraction());
observer.observe(document.body, { childList: true, subtree: true });