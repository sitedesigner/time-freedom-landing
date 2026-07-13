#!/usr/bin/env python3
"""Post-deal automation:
- Updates tracker revenue on close
- Creates deal package
- Sends summary to David
- Logs milestone
"""
import json, os, smtplib, ssl
from email.mime.text import MIMEText
from datetime import datetime
from pathlib import Path

BASE = Path(__file__).resolve().parent
TRACKER_PATH = Path.home() / "Documents" / "GoTechSolutions" / "time-freedom-landing" / "1m-tracker.json"
DEALS_DIR = Path.home() / "Documents" / "GoTechSolutions" / "time-freedom-landing" / "deals"

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

def notify_david_deal(deal):
    user = os.getenv("GMAIL_USER", "bizrunner@gmail.com")
    pwd = os.getenv("GMAIL_APP_PASSWORD", "")
    if not pwd:
        print("No Gmail app password configured, skipping deal notification")
        return
    body = (
        f"DEAL CLOSED\n\n"
        f"Deal ID: {deal['deal_id']}\n"
        f"Lead: {deal['lead_name']}\n"
        f"Email: {deal['email']}\n"
        f"Deal Value: ${deal['deal_value']:,}\n"
        f"Status: {deal['status']}\n\n"
        f"Review package: {deal.get('files', [DEALS_DIR / deal['deal_id'] / 'deal-summary.md'])}"
    )
    msg = MIMEText(body)
    msg["Subject"] = f"DEAL: {deal['lead_name']} @ ${deal['deal_value']:,}"
    msg["From"] = f"David Goecke <{user}>"
    msg["To"] = user
    context = ssl.create_default_context()
    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
            server.login(user, pwd)
            server.sendmail(user, user, msg.as_string())
    except Exception as e:
        print("Deal notification error:", e)

def close_deal(lead, amount=50000):
    ts = datetime.now().strftime('%Y%m%d-%H%M%S')
    name = lead.get('name', 'Lead')
    deal_id = f"DEAL-{ts}-{slugify(name)}"
    folder = DEALS_DIR / deal_id
    folder.mkdir(parents=True, exist_ok=True)

    summary = (
        f"# Deal Summary: {deal_id}\n\n"
        f"## Lead\n"
        f"- Name: {name}\n"
        f"- Email: {lead.get('email','')}\n"
        f"- Phone: {lead.get('phone','')}\n"
        f"- Challenge: {lead.get('challenge','')}\n\n"
        f"## Qualification\n"
        f"- Revenue: {lead.get('revenue','') or 'N/A'}\n"
        f"- Hours: {lead.get('hours','') or 'N/A'}\n"
        f"- Status: closed-won\n\n"
        f"## Financial\n"
        f"- Deal Value: ${amount:,}\n\n"
        f"## GHL\n"
        f"- Contact: {lead.get('contact_id') or 'N/A'}\n"
        f"- Opportunity: {lead.get('opportunity_id') or 'N/A'}\n\n"
        f"Generated: {datetime.now().isoformat()}\n"
    )
    (folder / "deal-summary.md").write_text(summary)

    pkg = {
        "deal_id": deal_id,
        "lead_name": name,
        "email": lead.get('email',''),
        "deal_value": amount,
        "status": "closed-won",
        "files": [str(folder / "deal-summary.md")],
        "created": datetime.now().isoformat(),
    }
    (folder / "package.json").write_text(json.dumps(pkg, indent=2))

    tracker = load_json(TRACKER_PATH)
    tracker["deals_won"] = tracker.get("deals_won", 0) + 1
    tracker["revenue_collected"] = tracker.get("revenue_collected", 0) + amount
    for lead_entry in tracker.get("leads", []):
        if lead_entry.get("email") == lead.get("email"):
            lead_entry["status"] = "closed-won"
            lead_entry["deal_value"] = amount
            break
    save_json(TRACKER_PATH, tracker)
    notify_david_deal(pkg)
    return pkg

if __name__ == '__main__':
    # Close all leads in tracker
    tracker = load_json(TRACKER_PATH)
    leads = tracker.get('leads', [])
    if not leads:
        print('No leads found')
    else:
        for lead in leads:
            amount = lead.get('deal_value', 50000)
            pkg = close_deal(lead, amount)
            print(f"Closed: {pkg['lead_name']} @ ${pkg['deal_value']:,} -> {pkg['deal_id']}")
        print('Done.')
