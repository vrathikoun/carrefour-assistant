from app.schemas import PageContext

def compact_context(ctx: PageContext, max_products: int = 8) -> str:
    lines = [
        f"Titre: {ctx.title}",
        f"URL: {ctx.url}",
        f"Type: {ctx.page_type}",
    ]

    if ctx.product:
        lines.append(f"Produit: {ctx.product.title} | Prix: {ctx.product.price}")

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