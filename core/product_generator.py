import json, os, random
from datetime import datetime
from pathlib import Path
from core.ai_client import AIClient

BASE_DIR = Path(__file__).parent.parent
PRODUCTS_DIR = BASE_DIR / "products"

PRODUCT_TYPES = ["prompt-pack", "template", "ebook", "code-bundle"]

NICHES = [
    "marketing digital", "software development", "business productivity",
    "content creation", "AI automation", "data science", "startups",
    "e-commerce", "social media management", "freelancing",
    "SEO optimization", "email marketing", "copywriting", "video production",
    "digital product creation", "personal finance", "online education",
    "Python programming", "web development", "prompt engineering",
]

class ProductGenerator:
    def __init__(self):
        self.ai = AIClient()

    def generate_prompt_pack(self, niche: str) -> str:
        return self.ai.generate(
            f"Eres un experto en prompt engineering para {niche}.",
            f"Genera 50 prompts profesionales en español para {niche}. "
            f"Cada prompt debe ser detallado y accionable.\n\n"
            f"Formato:\n"
            f"## Prompt 1\n"
            f"**Caso de uso:** [uso específico]\n"
            f"**Prompt:** [prompt completo y detallado]\n"
            f"**Resultado esperado:** [qué obtendrá el usuario]\n\n"
            f"Separa cada prompt con ---\n\n"
            f"Los prompts deben cubrir: creación de contenido, análisis, estrategia, optimización, investigación.",
            temperature=0.7,
            max_tokens=8192,
        )

    def generate_ebook(self, niche: str) -> str:
        return self.ai.generate(
            "Eres un autor experto en crear guías prácticas y accionables.",
            f"Escribe una guía completa sobre '{niche}' para emprendedores digitales.\n\n"
            f"Estructura:\n"
            f"# [Título atractivo]\n"
            f"## Introducción\n"
            f"## Capítulo 1: [concepto fundamental]\n"
            f"## Capítulo 2: [aplicación práctica]\n"
            f"## Capítulo 3: [estrategias avanzadas]\n"
            f"## Capítulo 4: [casos de éxito]\n"
            f"## Capítulo 5: [próximos pasos]\n"
            f"## Conclusión\n\n"
            f"Extensión: ~3000 palabras. En español. Incluye ejemplos concretos.",
            temperature=0.7,
        )

    def generate_code_bundle(self, niche: str) -> str:
        return self.ai.generate(
            "Eres un desarrollador Python senior experto en crear código reusable y profesional.",
            f"Crea un bundle de scripts Python para {niche}.\n\n"
            f"Incluye 5 scripts completos con:\n"
            f"- Docstrings explicativos\n"
            f"- Type hints\n"
            f"- Manejo de errores\n"
            f"- Logging\n"
            f"- Ejemplos de uso\n\n"
            f"Además un README.md explicando cada script.\n\n"
            f"Formato: código Python en bloques ```python.\n"
            f"Cada script debe ser funcional y listo para ejecutar.",
            temperature=0.5,
        )

    def generate_template(self, niche: str) -> str:
        return self.ai.generate(
            "Eres un experto en productividad y creación de plantillas digitales.",
            f"Diseña una plantilla detallada para {niche}.\n\n"
            f"Incluye:\n"
            f"- Estructura completa con secciones\n"
            f"- Instrucciones de uso paso a paso\n"
            f"- Ejemplos de cómo llenarla\n"
            f"- Tablas, checkboxes y formato profesional\n"
            f"- Tips de personalización\n\n"
            f"Formato markdown profesional. En español.",
            temperature=0.6,
        )

    def create_product_metadata(self, product_type: str, niche: str) -> dict:
        prices = {"prompt-pack": (7, 15), "template": (10, 20), "ebook": (8, 15), "code-bundle": (15, 25)}
        price_min, price_max = prices[product_type]

        meta = self.ai.generate_json(
            "Eres un copywriter experto en ventas de productos digitales. Genera metadata en español.",
            f"""Genera metadata para un producto digital tipo "{product_type}" sobre "{niche}".

Devuelve SOLO JSON SIN markdown:
{{
    "title_es": "título atractivo en español para este producto",
    "title_en": "title in english for this product",
    "tagline": "frase corta de marketing (max 12 palabras)",
    "description_es": "descripción de ventas en español (3 párrafos)",
    "description_en": "sales description in english (3 paragraphs)",
    "price_usd": número entre {price_min} y {price_max},
    "tags": ["3-5 tags relevantes"],
    "target_audience": "quién debería comprar esto",
    "what_they_get": "principal beneficio"
}}"""
        )
        return meta if isinstance(meta, dict) else {"title_es": niche, "price_usd": 9.99}

    def generate_thumbnail_text(self, product_type: str, niche: str, title: str) -> str:
        return self.ai.generate(
            "Eres un diseñador gráfico experto en thumbnails para productos digitales.",
            f"Crea texto para thumbnail de un {product_type} sobre {niche}.\n"
            f"Título del producto: {title}\n\n"
            f"Genera 3 opciones de texto corto y llamativo para el thumbnail (max 5 palabras cada una).",
            temperature=0.8,
        )

    def generate_full_product_batch(self, count: int = 15) -> list:
        products = []
        type_order = ["prompt-pack"] * 5 + ["template"] * 4 + ["ebook"] * 3 + ["code-bundle"] * 3

        for i in range(count):
            ptype = type_order[i]
            niche = random.choice(NICHES)
            print(f"  [{i+1}/{count}] Generating {ptype} on {niche}...")

            if ptype == "prompt-pack":
                content = self.generate_prompt_pack(niche)
            elif ptype == "ebook":
                content = self.generate_ebook(niche)
            elif ptype == "code-bundle":
                content = self.generate_code_bundle(niche)
            elif ptype == "template":
                content = self.generate_template(niche)
            else:
                continue

            meta = self.create_product_metadata(ptype, niche)
            thumbnail_text = self.generate_thumbnail_text(ptype, niche, meta.get("title_es", niche))

            product = {
                "id": f"{ptype}-{i+1:03d}",
                "type": ptype,
                "niche": niche,
                "title_es": meta.get("title_es", f"{ptype} sobre {niche}"),
                "title_en": meta.get("title_en", f"{ptype} about {niche}"),
                "tagline": meta.get("tagline", ""),
                "description_es": meta.get("description_es", ""),
                "description_en": meta.get("description_en", ""),
                "price_usd": meta.get("price_usd", 9.99),
                "tags": meta.get("tags", [niche]),
                "target_audience": meta.get("target_audience", ""),
                "what_they_get": meta.get("what_they_get", ""),
                "thumbnail_text": thumbnail_text,
                "content_preview": content[:3000],
                "full_content": content,
                "generated_at": datetime.now().isoformat(),
                "status": "ready",
            }
            products.append(product)

            product_dir = PRODUCTS_DIR / ptype.replace("-", "-") + "s"
            os.makedirs(product_dir, exist_ok=True)
            with open(product_dir / f"{product['id']}.json", "w") as f:
                json.dump(product, f, indent=2, ensure_ascii=False)

        # Save product catalog
        catalog_path = PRODUCTS_DIR / "catalog.json"
        with open(catalog_path, "w") as f:
            json.dump(products, f, indent=2, ensure_ascii=False)

        return products
