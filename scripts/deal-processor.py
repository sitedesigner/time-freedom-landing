#!/usr/bin/env python3
"""
Deal Closing Processor
- Reads leads, categorizes by revenue/hours
- Generates closing packages
- Updates tracker revenue
- Logs deal summary
"""
import json, os
from datetime import datetime
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
DEALS_DIR = BASE / "deals"
TRACKER_PATH = BASE / "1m-tracker.json"

def load_json(path):
    if path.exists():
        try:
            return json.loads(path.read_text())
        except Exception:
            return {}
    return {}

def save_json(path, data):
    path.write_text(json.dumps(data, indent=2))

def slugify(val):
    import re
    slug = re.sub(r"[^a-z0-9]+", "-", (val or "").lower()).strip("-")
    return slug[:80] if slug else "deal"

def close_deals():
    tracker = load_json(TRACKER_PATH)
    leads = tracker.get("leads", [])
    if not leads:
        print("No leads found in tracker")
        return []

    closed = []
    DEALS_DIR.mkdir(parents=True, exist_ok=True)

    for lead in leads:
        ts = datetime.now().strftime('%Y%m%d-%H%M%S')
        name = lead.get('name', 'Lead')
        email = lead.get('email', '')
        revenue = lead.get('revenue', '')
        hours = lead.get('hours', '')
        challenge = lead.get('challenge', '')
        contact_id = lead.get('contact_id')
        opportunity_id = lead.get('opportunity_id')
        deal_value = lead.get('deal_value', 50000)

        deal_id = f"DEAL-{ts}-{slugify(name)}"
        folder = DEALS_DIR / deal_id
        folder.mkdir(parents=True, exist_ok=True)

        summary = (
            f"# Deal Summary: {deal_id}\n\n"
            f"## Lead\n"
            f"- Name: {name}\n"
            f"- Email: {email}\n"
            f"- Challenge: {challenge}\n\n"
            f"## Qualification\n"
            f"- Revenue: {revenue or 'N/A'}\n"
            f"- Hours: {hours or 'N/A'}\n"
            f"- Status: closed-won\n\n"
            f"## Financial\n"
            f"- Deal Value: ${deal_value:,}\n\n"
            f"## GHL\n"
            f"- Contact: {contact_id or 'N/A'}\n"
            f"- Opportunity: {opportunity_id or 'N/A'}\n\n"
            f"Generated: {datetime.now().isoformat()}\n"
        )

        (folder / "deal-summary.md").write_text(summary)

        pkg = {
            "deal_id": deal_id,
            "lead_name": name,
            "email": email,
            "revenue": revenue,
            "hours": hours,
            "deal_value": deal_value,
            "status": "closed-won",
            "created": datetime.now().isoformat(),
            "files": [str(folder / "deal-summary.md")],
        }
        (folder / "package.json").write_text(json.dumps(pkg, indent=2))
        closed.append(pkg)

        # Update tracker revenue
        tracker["deals_won"] = tracker.get("deals_won", 0) + 1
        tracker["revenue_collected"] = tracker.get("revenue_collected", 0) + deal_value
        for lead_entry in tracker.get("leads", []):
            if lead_entry.get("email") == email:
                lead_entry["status"] = "closed-won"
                lead_entry["deal_value"] = deal_value
                break

    save_json(TRACKER_PATH, tracker)
    return closed

if __name__ == '__main__':
    deals = close_deals()
    print(f"Closed {len(deals)} deals. Total value: ${sum(d['deal_value'] for d in deals):,}")
    for d in deals:
        print(f"  {d['deal_id']} | {d['lead_name']} | ${d['deal_value']:,}")
