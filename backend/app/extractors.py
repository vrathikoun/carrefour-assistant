import re
import json
from app.schemas import PageContext

def compact_context(ctx: PageContext, max_products: int = 8) -> str:
    lines = [
        f"Titre: {ctx.title}",
        f"URL: {ctx.url}",
        f"Type: {ctx.page_type}",
    ]

    if ctx.product:
        lines.append(f"Produit: {ctx.product.title} | Prix: {ctx.product.price}")

    if ctx.recommended_products:
        lines.append("Produits recommandés / similaires:")
        for i, p in enumerate(ctx.recommended_products[:max_products], start=1):
            url_part = f" | {p.url}" if getattr(p, "url", None) else ""
            lines.append(f"- {i}. {p.title} | {p.price}{url_part}")

    if ctx.products:
        lines.append("Produits visibles:")
        for i, p in enumerate(ctx.products[:max_products], start=1):
            lines.append(f"- {i}. {p.title} | {p.price}")

    if ctx.promos:
        lines.append("Promos visibles:")
        for promo in (ctx.promos[:10]):
            lines.append(f"- {promo}")

    if ctx.bodyText:
        txt = ctx.bodyText.strip().replace("\n", " ")
        lines.append(f"Texte page (extrait): {txt[:600]}")

    return "\n".join(lines)

def extract_json_object(text: str) -> dict:
    """
    Extract the first JSON object found in text, robust to code fences.
    """
    if not text:
        raise ValueError("Empty model output")

    # Remove ```json fences if present
    text = re.sub(r"^```(?:json)?\s*", "", text.strip())
    text = re.sub(r"\s*```$", "", text.strip())

    # Find first {...} block
    m = re.search(r"\{.*\}", text, flags=re.DOTALL)
    if not m:
        raise ValueError("No JSON object found in output")

    return json.loads(m.group(0))