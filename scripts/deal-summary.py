#!/usr/bin/env python3
"""
Deal Summary Generator
- Reads leads from tracker
- Generates formatted deal summaries
- Exports to markdown for review
"""
import json
import os
from datetime import datetime
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent / "time-freedom-landing"
TRACKER_PATH = BASE / "1m-tracker.json"
DEALS_DIR = BASE / "deals"


def load_json(path):
    if path.exists():
        try:
            return json.loads(path.read_text())
        except Exception:
            return {}
    return {}


def generate_deal_summary(lead, deal_id=None):
    """Generate a formatted deal summary dict."""
    deal = {
        "deal_id": deal_id or f"DEAL-{datetime.now().strftime('%Y%m%d-%H%M%S')}",
        "timestamp": datetime.now().isoformat(),
        "lead_name": lead.get("name", ""),
        "email": lead.get("email", ""),
        "phone": lead.get("phone", ""),
        "revenue_range": lead.get("revenue", ""),
        "hours_range": lead.get("hours", ""),
        "challenge": lead.get("challenge", ""),
        "contact_id": lead.get("contact_id"),
        "opportunity_id": lead.get("opportunity_id"),
        "deal_value": lead.get("deal_value", 50000),
        "status": lead.get("status", "lead"),
        "stage": "Applied",
        "next_action": "Review application",
        "notes": lead.get("notes", ""),
    }
    return deal


def save_deal_summary(deal):
    """Save deal summary as markdown."""
    DEALS_DIR.mkdir(parents=True, exist_ok=True)
    md_path = DEALS_DIR / f"{deal['deal_id']}.md"
    md = f"""# Deal Summary: {deal['deal_id']}

## Lead Info
- **Name:** {deal['lead_name']}
- **Email:** {deal['email']}
- **Phone:** {deal['phone']}
- **Challenge:** {deal['challenge']}

## Qualification
- **Revenue Range:** {deal['revenue_range']}
- **Hours Worked:** {deal['hours_range']}
- **Status:** {deal['status']}
- **GHL Contact:** {deal['contact_id'] or 'None'}
- **GHL Opportunity:** {deal['opportunity_id'] or 'None'}

## Deal
- **Deal ID:** {deal['deal_id']}
- **Value:** ${deal['deal_value']:,}
- **Stage:** {deal['stage']}
- **Next Action:** {deal['next_action']}
- **Notes:** {deal['notes']}

## Generated
- **Timestamp:** {deal['timestamp']}
- **Automation:** Time Freedom Landing Page
"""
    md_path.write_text(md)
    print(f"Saved deal summary: {md_path}")
    return md_path


def build_all_deal_summaries():
    """Generate summaries for all leads in tracker."""
    tracker = load_json(TRACKER_PATH)
    leads = tracker.get("leads", [])
    summaries = []
    for lead in leads:
        deal = generate_deal_summary(lead)
        md_path = save_deal_summary(deal)
        summaries.append({
            "deal_id": deal["deal_id"],
            "name": deal["lead_name"],
            "email": deal["email"],
            "value": deal["deal_value"],
            "stage": deal["stage"],
            "file": str(md_path),
        })
    return summaries


if __name__ == "__main__":
    summaries = build_all_deal_summaries()
    print(f"\nGenerated {len(summaries)} deal summaries:")
    for s in summaries:
        print(f"  {s['deal_id']} | {s['name']} | ${s['value']:,} | {s['stage']}")
