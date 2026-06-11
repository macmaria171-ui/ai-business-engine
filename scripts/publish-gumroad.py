#!/usr/bin/env python3
import sys, json, os, requests
from pathlib import Path

BASE = Path(__file__).parent.parent
GUMROAD_API = "https://api.gumroad.com/v2"

def get_catalog():
    cat = BASE / "products" / "catalog.json"
    if not cat.exists():
        return []
    return json.loads(cat.read_text())

def get_product_content(pid):
    for subdir in ["prompt-packs", "templates", "ebooks", "code-bundles"]:
        fp = BASE / "products" / subdir / f"{pid}.json"
        if fp.exists():
            data = json.loads(fp.read_text())
            return data.get("full_content", "")
    return ""

def publish_all():
    token = os.environ.get("GUMROAD_TOKEN", "")
    if not token:
        print("❌ GUMROAD_TOKEN not set")
        return 1

    products = get_catalog()
    if not products:
        print("❌ No products found")
        return 1

    # Get existing products to avoid duplicates
    existing = requests.get(f"{GUMROAD_API}/products?access_token={token}", timeout=15).json()
    existing_names = {p["name"] for p in existing.get("products", [])}

    results = []
    for i, p in enumerate(products, 1):
        name = p.get("title_es", "Product")
        if name in existing_names:
            print(f"  [{i}/{len(products)}] ⏭️  Already published: {name[:50]}")
            results.append({"id": p["id"], "status": "exists"})
            continue

        pid = p["id"]
        content = get_product_content(pid)
        price_cents = int(float(p.get("price_usd", 9.99)) * 100)
        tags = ",".join(p.get("tags", [])[:4])

        description = f"# {name}\n\n{p.get('tagline', '')}\n\n---\n\n## 📋 Descripción\n{content[:3000]}\n\n---\n\n## 🎯 ¿Para quién es?\n{p.get('target_audience', 'Para emprendedores digitales')}\n\n## 💡 ¿Qué obtendrás?\n{p.get('what_they_get', 'Contenido premium')}"

        try:
            resp = requests.post(
                f"{GUMROAD_API}/products?access_token={token}",
                data={
                    "name": name,
                    "description": description,
                    "price": price_cents,
                    "currency": "usd",
                    "tags": tags,
                    "customizable_price": "true",
                    "require_shipping": "false",
                },
                timeout=30,
            )
            data = resp.json()
            if data.get("success"):
                product_url = data.get("product", {}).get("short_url", "")
                print(f"  [{i}/{len(products)}] ✅ ${p['price_usd']:.0f} - {name[:50]} - {product_url}")
                results.append({"id": pid, "status": "published", "url": product_url})
            else:
                err = data.get("message", resp.text[:200])
                print(f"  [{i}/{len(products)}] ❌ {name[:40]}: {err}")
                results.append({"id": pid, "status": "error", "error": err})
        except Exception as e:
            print(f"  [{i}/{len(products)}] ❌ {name[:40]}: {e}")
            results.append({"id": pid, "status": "error", "error": str(e)})

    # Save log
    log = BASE / "products" / "publish_log.json"
    log.write_text(json.dumps({"date": __import__("datetime").datetime.now().isoformat(), "results": results}, indent=2, ensure_ascii=False))

    ok = sum(1 for r in results if r["status"] in ["published", "exists"])
    print(f"\n✅ Publicados: {ok}/{len(products)}")

    # Show URLs
    urls = [r["url"] for r in results if "url" in r]
    if urls:
        print(f"\n🔗 Enlaces:")
        for u in urls:
            print(f"   {u}")
    return 0

if __name__ == "__main__":
    sys.exit(publish_all())
