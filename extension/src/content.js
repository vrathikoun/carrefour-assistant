// --- Carrefour Content Script (robust POC) ---

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
  // Carrefour search page: ul#data-plp_produits > li.product-list-grid__item > article
  const list = document.querySelector("#data-plp_produits");
  if (list) {
    const items = Array.from(list.querySelectorAll("li.product-list-grid__item article"))
      .slice(0, 12);

    const products = [];
    for (const article of items) {
      // Title
      const titleEl =
        article.querySelector('[data-testid="product-card-title"] h3') ||
        article.querySelector('[data-testid="product-card-title"]') ||
        article.querySelector("h3");

      const title = getText(titleEl);

      // Price (Carrefour often splits number + € in a span)
      const priceEl =
        article.querySelector('[data-testid*="price"]') ||
        article.querySelector("p[class*='base-price']") ||
        article.querySelector("[class*='price']");

      let price = "";
      if (priceEl) {
        price = (priceEl.textContent || "").replace(/\s+/g, " ").trim();
      }

      if (title && price) products.push({ title, price });
    }

    if (products.length) return products.slice(0, 10);
  }

  // Fallback generic heuristic
  const cards = Array.from(
    document.querySelectorAll("article, li, div[class*='product'], div[class*='item']")
  )
    .filter(
      (n) =>
        n.querySelector &&
        (n.querySelector("[class*=price]") || n.querySelector("a"))
    )
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
  const nodes = Array.from(document.querySelectorAll("section, article, div"))
    .filter((n) => /promo|offre|réduction|%/i.test(getText(n)))
    .slice(0, 12);

  return nodes
    .map((n) => getText(n))
    .filter((t) => t.length > 20)
    .slice(0, 6);
}

function extractProduct() {
  const title = getText(document.querySelector("h1"));
  const price = getText(document.querySelector("[class*=price], [data-testid*=price]"));
  const desc = getText(document.querySelector("[class*=description], main"));
  return {
    title,
    price,
    desc: (desc || "").slice(0, 1200),
  };
}

function extractRecommendedProducts(max = 8) {
  const current = location.pathname;

  // candidate links to other product pages
  const links = Array.from(document.querySelectorAll('a[href*="/p/"]'))
    .map((a) => {
      const href = a.getAttribute("href") || "";
      // normalize to absolute
      const url = href.startsWith("http") ? href : new URL(href, location.origin).toString();
      return { a, url, href };
    })
    .filter((x) => {
      try {
        const u = new URL(x.url);
        return u.pathname.includes("/p/") && u.pathname !== current;
      } catch {
        return false;
      }
    });

  const seen = new Set();
  const out = [];

  for (const { a, url } of links) {
    if (seen.has(url)) continue;

    // nearest "card" container
    const card =
      a.closest("article") ||
      a.closest("li") ||
      a.closest("div");

    if (!card) continue;

    // title heuristics inside the card
    const titleEl =
      card.querySelector('[data-testid="product-card-title"] h3') ||
      card.querySelector('[data-testid="product-card-title"]') ||
      card.querySelector("h3") ||
      card.querySelector("h2") ||
      a;

    const title = getText(titleEl);

    // price heuristics inside the card
    const priceEl =
      card.querySelector('[data-testid*="price"]') ||
      card.querySelector("p[class*='base-price']") ||
      card.querySelector("[class*='price']");

    const price = normPrice(priceEl?.textContent || "");

    // keep only useful entries
    if (title && price) {
      out.push({ title, price, url });
      seen.add(url);
      if (out.length >= max) break;
    }
  }

  return out;
}

function extractContext() {
  const page_type = detectPageType();
  const base = {
    url: location.href,
    title: document.title,
    page_type,
  };

  if (page_type === "HOME") return { ...base, promos: extractHomePromos() };
  if (page_type === "SEARCH") return { ...base, products: extractSearchProducts() };
  if (page_type === "PRODUCT") return { ...base, product: extractProduct() };

  // fallback text
  const bodyText = getText(document.body).slice(0, 3000);
  return { ...base, bodyText };
}

function debounce(func, wait) {
  let timeout;
  return function (...args) {
    clearTimeout(timeout);
    timeout = setTimeout(() => func.apply(this, args), wait);
  };
}

// ---- Robust sendMessage (handles "Extension context invalidated") ----
let observer = null;

function safeSendContext() {
  const payload = extractContext();

  try {
    chrome.runtime.sendMessage({ type: "PAGE_CONTEXT", payload }, () => {
      // if runtime invalidated or background missing, chrome.runtime.lastError is set
      if (chrome.runtime.lastError) {
        console.warn("sendMessage failed:", chrome.runtime.lastError.message);
        // stop observer to avoid log spam
        try {
          observer?.disconnect();
        } catch (e) {}
      }
    });
  } catch (e) {
    console.warn("Extension context invalidated (caught):", e);
    try {
      observer?.disconnect();
    } catch (err) {}
  }
}

// Debounced main extraction
const runExtraction = debounce(() => {
  safeSendContext();
}, 800);

// 1) initial
runExtraction();

// 2) observe DOM changes (SPA / lazy loading)
try {
  observer = new MutationObserver(() => runExtraction());
  observer.observe(document.body, { childList: true, subtree: true });
} catch (e) {
  console.warn("MutationObserver failed:", e);
}
