from app.schemas import PageContext

def suggestions_rule_based(ctx: PageContext) -> list[str]:
    pt = (ctx.page_type or "OTHER").upper()

    if pt == "HOME":
        return [
            "Quelles sont les meilleures promos du moment ?",
            "Quels produits sont les plus mis en avant aujourd’hui ?",
            "Peux-tu proposer un panier “courses de la semaine” économique ?"
        ]

    if pt == "SEARCH" and ctx.products:
        names = [p.title for p in ctx.products[:3]]
        return [
            f"Compare-moi {names[0]} vs {names[1]} (prix, quantité, valeur).",
            "Lequel est le moins cher au kilo / litre parmi les produits visibles ?",
            f"Trouve une alternative moins chère à {names[0]}."
        ]

    if pt == "PRODUCT" and ctx.product:
        name = ctx.product.title
        return [
            f"{name} vaut-il son prix ? Donne les points clés.",
            f"Donne-moi des alternatives à {name} (moins cher / meilleure compo).",
            f"Idées de recettes / usages avec {name}."
        ]

    return [
        "Résume cette page en 5 points.",
        "Que puis-je faire sur cette page ?",
        "Quels éléments importants dois-je regarder ici ?"
    ]
