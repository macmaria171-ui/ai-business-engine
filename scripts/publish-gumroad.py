#!/usr/bin/env python3
"""
Gumroad Publisher - Creates product listings on Gumroad via API.
Uses Gumroad API: https://app.gumroad.com/api
"""
import sys, json, os, requests
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

GUMROAD_API = "https://api.gumroad.com/v2"

def get_products():
    catalog = Path(__file__).parent.parent / "products" / "catalog.json"
    if not catalog.exists():
        print("❌ No catalog.json found. Run generate-products.py first.")
        return []
    with open(catalog) as f:
        return json.load(f)

def publish_product(product: dict) -> dict:
    token = os.environ.get("GUMROAD_TOKEN", "")
    email = os.environ.get("GUMROAD_EMAIL", "")

    if not token:
        print(f"  ⚠️  No GUMROAD_TOKEN set. Skipping {product['id']}")
        return {"status": "skipped", "reason": "no_token"}

    payload = {
        "access_token": token,
        "name": product.get("title_es", product.get("title_en", "Product")),
        "description": product.get("description_es", product.get("description_en", "")),
        "price": int(float(product.get("price_usd", 9.99)) * 100),
        "currency": "usd",
        "tags": ",".join(product.get("tags", [])),
        "customizable_price": "true",
        "max_purchase_count": None,
    }

    try:
        resp = requests.post(f"{GUMROAD_API}/products", json=payload, timeout=30)
        if resp.status_code in [200, 201]:
            data = resp.json()
            print(f"  ✅ Published: {payload['name']} (${product['price_usd']})")
            return {"status": "published", "gumroad_id": data.get("product", {}).get("id")}
        else:
            print(f"  ❌ Failed: {payload['name']} - {resp.status_code}: {resp.text[:200]}")
            return {"status": "error", "error": resp.text[:200]}
    except Exception as e:
        print(f"  ❌ Exception: {e}")
        return {"status": "error", "error": str(e)}

def main():
    print("📦 Gumroad Publisher")
    products = get_products()
    if not products:
        print("No products to publish.")
        return 1

    print(f"Found {len(products)} products in catalog")

    published = []
    for p in products:
        result = publish_product(p)
        published.append(result)

    stats = {"published": sum(1 for r in published if r["status"] == "published"), "total": len(published)}
    print(f"\n✅ Published: {stats['published']}/{stats['total']}")

    # Save publish log
    log_path = Path(__file__).parent.parent / "products" / "publish_log.json"
    with open(log_path, "w") as f:
        json.dump({"date": __import__("datetime").datetime.now().isoformat(), "results": published}, f, indent=2)

    return 0

if __name__ == "__main__":
    sys.exit(main())
