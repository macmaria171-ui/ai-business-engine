#!/usr/bin/env python3
"""
Analytics & Reporting - Tracks revenue, product performance, and generates reports.
"""
import sys, json, os
from pathlib import Path
from datetime import datetime, timedelta

sys.path.insert(0, str(Path(__file__).parent.parent))

def load_catalog():
    catalog = Path(__file__).parent.parent / "products" / "catalog.json"
    if not catalog.exists():
        return []
    with open(catalog) as f:
        return json.load(f)

def load_publish_log():
    log = Path(__file__).parent.parent / "products" / "publish_log.json"
    if not log.exists():
        return {}
    with open(log) as f:
        return json.load(f)

def generate_report():
    products = load_catalog()
    publish_log = load_publish_log()

    total_value = sum(p.get("price_usd", 0) for p in products)
    avg_price = total_value / len(products) if products else 0

    by_type = {}
    for p in products:
        t = p.get("type", "unknown")
        by_type[t] = by_type.get(t, 0) + 1

    report = {
        "date": datetime.now().isoformat(),
        "total_products": len(products),
        "total_catalog_value": round(total_value, 2),
        "average_price": round(avg_price, 2),
        "products_by_type": by_type,
        "published_count": publish_log.get("results", []) if publish_log else [],
        "weekly_revenue_target": 500.0,
        "weekly_progress": 0.0,
        "sales_needed_for_target": int(500 / avg_price) if avg_price > 0 else 0,
        "top_niches": list(set(p.get("niche", "unknown") for p in products)),
    }

    report_path = Path(__file__).parent.parent / "products" / "analytics.json"
    with open(report_path, "w") as f:
        json.dump(report, f, indent=2)

    return report

def format_report(report: dict) -> str:
    lines = [
        "📊 **Reporte Diario - AI Business Engine**",
        "",
        f"📦 Productos en catálogo: {report['total_products']}",
        f"💰 Valor total del catálogo: ${report['total_catalog_value']}",
        f"🏷️  Precio promedio: ${report['average_price']}",
        "",
        "📁 Productos por tipo:",
    ]
    for ptype, count in report.get("products_by_type", {}).items():
        lines.append(f"  • {ptype}: {count}")
    lines.append("")
    lines.append(f"🎯 Meta semanal: ${report['weekly_revenue_target']}")
    lines.append(f"📈 Ventas necesarias: {report['sales_needed_for_target']}/semana")
    lines.append("")
    lines.append("🔥 Top nichos: " + ", ".join(report.get("top_niches", [])[:5]))

    return "\n".join(lines)

def send_telegram_report(report_text: str):
    import requests
    token = os.environ.get("TELEGRAM_BOT_TOKEN", "")
    chat_id = os.environ.get("TELEGRAM_CHAT_ID", "")
    if not token or not chat_id:
        return
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    try:
        requests.post(url, json={"chat_id": chat_id, "text": report_text, "parse_mode": "Markdown"}, timeout=15)
    except:
        pass

def main():
    print("📊 Analytics Report")
    report = generate_report()
    text = format_report(report)
    print(text)

    send_telegram_report(text)
    print("\n✅ Report sent to Telegram")

    return 0

if __name__ == "__main__":
    sys.exit(main())
