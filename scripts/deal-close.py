#!/usr/bin/env python3
"""Deal Close Automation - generates closing package, updates tracker, notifies David."""
import json
import os
import smtplib
import ssl
from email.mime.text import MIMEText
from datetime import datetime
from pathlib import Path

BASE = Path(__file__).resolve().parent
DEALS_DIR = Path.home() / "Documents" / "GoTechSolutions" / "time-freedom-landing" / "deals"
TRACKER_PATH = Path.home() / "Documents" / "GoTechSolutions" / "time-freedom-landing" / "1m-tracker.json"
GMAIL_USER = os.getenv("GMAIL_USER", "bizrunner@gmail.com")
GMAIL_APP_PASSWORD = os.getenv("GMAIL_APP_PASSWORD", "")


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


def build_closing_package(lead, close_amount=50000):
    ts = datetime.now().strftime('%Y%m%d-%H%M%S')
    name = lead.get('name', 'Lead')
    deal_id = f"DEAL-{ts}-{slugify(name)}"
    folder = DEALS_DIR / deal_id
    folder.mkdir(parents=True, exist_ok=True)

    summary = f"""# Deal Closing Summary: {deal_id}

## Lead
- Name: {name}
- Email: {lead.get('email','')}
- Phone: {lead.get('phone','')}
- Challenge: {lead.get('challenge','')}

## Qualification
- Revenue Range: {lead.get('revenue','') or 'N/A'}
- Hours Worked: {lead.get('hours','') or 'N/A'}
- Status: closed-won

## Financial
- Deal Value: ${close_amount:,}
- Collection Method: ACH / Wire
- Time Freedom Coaching: $50K-$100K/yr

## GHL
- Contact ID: {lead.get('contact_id') or 'N/A'}
- Opportunity ID: {lead.get('opportunity_id') or 'N/A'}

## Next Steps
1. Send welcome packet
2. Schedule kickoff call
3. Setup 90-day execution plan
4. Begin onboarding

Generated: {datetime.now().isoformat()}
Closing By: David Goecke
"""
    (folder / "deal-summary.md").write_text(summary)

    package = {
        "deal_id": deal_id,
        "lead_name": name,
        "email": lead.get('email',''),
        "phone": lead.get('phone',''),
        "revenue": lead.get('revenue',''),
        "hours": lead.get('hours',''),
        "deal_value": close_amount,
        "status": "closed-won",
        "files": [str(folder / "deal-summary.md")],
        "created": datetime.now().isoformat(),
    }
    (folder / "package.json").write_text(json.dumps(package, indent=2))
    return package


def notify_david(deal):
    if not GMAIL_APP_PASSWORD:
        print("No Gmail app password configured, skipping email notification")
        return
    body = f"CLOSED DEAL\n\nDeal ID: {deal['deal_id']}\nLead: {deal['lead_name']}\nEmail: {deal['email']}\nValue: ${deal['deal_value']:,}\nStatus: {deal['status']}\n\nReview deal package in /deals/{deal['deal_id']}/"
    msg = MIMEText(body)
    msg["Subject"] = f"DEAL CLOSED: {deal['lead_name']} - ${deal['deal_value']:,}"
    msg["From"] = f"David Goecke <{GMAIL_USER}>"
    msg["To"] = GMAIL_USER
    context = ssl.create_default_context()
    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
            server.login(GMAIL_USER, GMAIL_APP_PASSWORD)
            server.sendmail(GMAIL_USER, GMAIL_USER, msg.as_string())
        print(f"Notification sent to David for deal {deal['deal_id']}")
    except Exception as e:
        print(f"Notification email error: {e}")


def process_deal_close(lead, close_amount=50000):
    """Process a deal close from a lead."""
    package = build_closing_package(lead, close_amount)
    notify_david(package)

    # Update tracker
    tracker = load_json(TRACKER_PATH)
    tracker["deals_won"] = tracker.get("deals_won", 0) + 1
    tracker["revenue_collected"] = tracker.get("revenue_collected", 0) + close_amount
    # Update lead status if exists
    for lead_entry in tracker.get("leads", []):
        if lead_entry.get("email") == lead.get("email"):
            lead_entry["status"] = "closed-won"
            lead_entry["deal_value"] = close_amount
            break
    save_json(TRACKER_PATH, tracker)
    return package


if __name__ == "__main__":
    tracker = load_json(TRACKER_PATH)
    leads = tracker.get("leads", [])
    if not leads:
        print("No leads found - create test leads first")
    else:
        print(f"Processing {len(leads)} deal closes...")
        for lead in leads:
            if not lead.get("email"):
                continue
            pkg = process_deal_close(lead)
            print(f"  Closed: {pkg['lead_name']} @ ${pkg['deal_value']:,} -> {pkg['deal_id']}")
        print("All leads processed.")
