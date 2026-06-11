#!/usr/bin/env python3
"""
Marketing Automation - Generates and posts marketing content.
Posts to Telegram for now (Twitter API requires extra setup).
"""
import sys, json, os, requests, random
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent.parent))
from core.ai_client import AIClient

POST_TEMPLATES = [
    "🚀 **Nuevo producto:** {title}\n{tagline}\n\n💻 Precio: ${price}\n\n{cta}",
    "🔥 **¡Oferta especial!**\n\n{title}\n{tagline}\n\n💰 Solo ${price}\n\n{cta}",
    "📢 **¿Necesitas {benefit}?**\n\n{title} te ayuda a:\n• {point1}\n• {point2}\n• {point3}\n\n🎯 ${price}\n\n{cta}",
    "💡 **Tip del día:** {tip}\n\n🎁 Si te gustó, mira {title} por solo ${price}\n\n{cta}",
    "📚 **Recomendación:** {title}\n{tagline}\n\n✅ {what_they_get}\n\n💰 ${price}\n\n{cta}",
]

def load_catalog():
    catalog = Path(__file__).parent.parent / "products" / "catalog.json"
    if not catalog.exists():
        return []
    with open(catalog) as f:
        return json.load(f)

def send_telegram(message: str):
    token = os.environ.get("TELEGRAM_BOT_TOKEN", "")
    chat_id = os.environ.get("TELEGRAM_CHAT_ID", "")
    if not token or not chat_id:
        return {"status": "skipped", "reason": "no_telegram_config"}
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    try:
        resp = requests.post(url, json={"chat_id": chat_id, "text": message, "parse_mode": "Markdown"}, timeout=15)
        return {"status": "sent" if resp.status_code == 200 else "error", "code": resp.status_code}
    except Exception as e:
        return {"status": "error", "error": str(e)}

def generate_post(product: dict) -> str:
    ai = AIClient()
    tip = ai.generate("Eres un experto en marketing digital.", f"Genera un tip corto y útil sobre {product.get('niche', 'marketing')}. Máximo 2 oraciones.", temperature=0.7)
    post = random.choice(POST_TEMPLATES).format(
        title=product.get("title_es", product.get("title_en", "Producto")),
        tagline=product.get("tagline", ""),
        price=product.get("price_usd", 9.99),
        benefit=product.get("what_they_get", product.get("niche", "")),
        point1="Ahorra horas de trabajo",
        point2="Resultados profesionales",
        point3="Fácil de implementar",
        tip=tip[:100],
        what_they_get=product.get("what_they_get", ""),
        cta="🔗 Disponible ya en Gumroad",
        niche=product.get("niche", ""),
    )
    return post

def main():
    print("📢 Marketing Engine")
    products = load_catalog()
    if not products:
        print("No products found. Run generate-products.py first.")
        return 1

    selected = random.sample(products, min(3, len(products)))
    results = []

    for product in selected:
        post = generate_post(product)
        result = send_telegram(post)
        result["product_id"] = product["id"]
        results.append(result)
        print(f"  {'✅' if result.get('status') == 'sent' else '❌'} {product['id']}: {result.get('status')}")

    print(f"\n✅ Posted {sum(1 for r in results if r.get('status') == 'sent')}/{len(results)} posts")
    return 0

if __name__ == "__main__":
    sys.exit(main())
