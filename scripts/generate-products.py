#!/usr/bin/env python3
import sys, json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from core.product_generator import ProductGenerator

def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--count", "-c", type=int, default=15, help="Number of products")
    args = parser.parse_args()

    print(f"🚀 Generating {args.count} products...")
    gen = ProductGenerator()
    products = gen.generate_full_product_batch(args.count)

    print(f"\n✅ Generated {len(products)} products:")
    for p in products:
        print(f"  📦 {p['id']}: {p['title_es'][:60]} — ${p['price_usd']}")

    print(f"\n📁 Catalog saved: products/catalog.json")
    return 0

if __name__ == "__main__":
    sys.exit(main())
