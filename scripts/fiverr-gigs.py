#!/usr/bin/env python3
"""
Fiverr Gig Manager - Creates and optimizes Fiverr gig listings via AI.
Fiverr doesn't have a public create-gig API, so this generates the gig content
for manual publishing and tracks optimization suggestions.
"""
import sys, json, os
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from core.ai_client import AIClient

GIGS = [
    {
        "title": "I will write high quality AI content for your business",
        "category": "Writing & Translation",
        "subcategory": "Content Writing",
        "packages": [
            {"name": "Basic", "price": 15, "delivery": 2, "description": "500 words of AI-optimized content"},
            {"name": "Standard", "price": 35, "delivery": 1, "description": "1500 words + SEO keywords + headings"},
            {"name": "Premium", "price": 75, "delivery": 1, "description": "5000 words + SEO + images + research"},
        ],
    },
    {
        "title": "I will create custom ChatGPT prompt packs for your niche",
        "category": "Writing & Translation",
        "subcategory": "Creative Writing",
        "packages": [
            {"name": "Basic", "price": 10, "delivery": 1, "description": "25 custom prompts for your niche"},
            {"name": "Standard", "price": 25, "delivery": 2, "description": "100 prompts + categories + use cases"},
            {"name": "Premium", "price": 50, "delivery": 3, "description": "500 prompts + guide + priority support"},
        ],
    },
    {
        "title": "I will develop custom Python scripts and automations",
        "category": "Programming & Tech",
        "subcategory": "Python",
        "packages": [
            {"name": "Basic", "price": 20, "delivery": 3, "description": "Simple script (up to 100 lines)"},
            {"name": "Standard", "price": 50, "delivery": 5, "description": "Medium automation with error handling"},
            {"name": "Premium", "price": 120, "delivery": 7, "description": "Full automation system with GUI/API"},
        ],
    },
    {
        "title": "I will create AI powered business automations with n8n",
        "category": "Programming & Tech",
        "subcategory": "Automation",
        "packages": [
            {"name": "Basic", "price": 25, "delivery": 2, "description": "Simple 2-step automation"},
            {"name": "Standard", "price": 60, "delivery": 4, "description": "Multi-step workflow with AI integration"},
            {"name": "Premium", "price": 150, "delivery": 7, "description": "Complete business automation system"},
        ],
    },
    {
        "title": "I will design digital products and templates for your business",
        "category": "Design & Creative",
        "subcategory": "Graphic Design",
        "packages": [
            {"name": "Basic", "price": 15, "delivery": 2, "description": "1 custom template/design"},
            {"name": "Standard", "price": 40, "delivery": 3, "description": "3 templates + customization guide"},
            {"name": "Premium", "price": 80, "delivery": 5, "description": "10 templates full brand kit"},
        ],
    },
]

def optimize_gig_description(gig: dict) -> str:
    ai = AIClient()
    return ai.generate(
        "Eres un experto en Fiverr SEO y copywriting de gigs. Genera descripciones que conviertan.",
        f"""Genera la descripción completa para este gig de Fiverr:

Título: {gig['title']}
Categoría: {gig['category']}
Paquetes: {json.dumps(gig['packages'], indent=2)}

Incluye:
1. Descripción principal convincente (qué ofrece, por qué elegirme)
2. FAQs (3 preguntas comunes con respuestas)
3. Requisitos del comprador (qué necesito para empezar)

En español. Formato markdown profesional. Máximo 500 palabras."""
    )

def main():
    print("🎯 Fiverr Gig Manager")
    print(f"Username: {os.environ.get('FIVERR_USERNAME', 'not set')}")

    gigs_dir = Path(__file__).parent.parent / "fiverr" / "gigs"
    gigs_dir.mkdir(parents=True, exist_ok=True)

    for i, gig in enumerate(GIGS):
        print(f"\n  [{i+1}/{len(GIGS)}] Optimizing: {gig['title'][:50]}...")
        description = optimize_gig_description(gig)

        gig_data = {**gig, "description": description, "optimized_at": __import__("datetime").datetime.now().isoformat()}

        gig_file = gigs_dir / f"gig-{i+1:02d}.json"
        with open(gig_file, "w") as f:
            json.dump(gig_data, f, indent=2, ensure_ascii=False)

        print(f"    ✅ Saved: {gig_file.name}")

    print(f"\n✅ {len(GIGS)} gigs prepared for publishing")
    print("📌 Note: Fiverr requires manual gig creation via their platform.")
    print("   Copy the descriptions from fiverr/gigs/ to Fiverr dashboard.")
    print(f"   Login as: {os.environ.get('FIVERR_USERNAME', 'jmhs1994')}")

    return 0

if __name__ == "__main__":
    sys.exit(main())
