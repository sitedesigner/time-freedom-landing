#!/usr/bin/env python3
"""
Deal Router
- Reads leads from tracker
- Applies qualification rules
- Updates GHL tags/opportunity stage based on revenue + hours
"""
import json
import os
from datetime import datetime
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent / "time-freedom-landing"
TRACKER_PATH = BASE / "1m-tracker.json"


def load_json(path):
    if path.exists():
        try:
            return json.loads(path.read_text())
        except Exception:
            return {}
    return {}


def qualify(revenue, hours):
    """Return qualification tier: hot, qualified, borderline, unqualified."""
    r = revenue.lower() if revenue else ""
    h = hours.lower() if hours else ""

    r_high = "250k" in r or "500k" in r or "1m" in r or "100k" in r and "500k" in r
    # Better checks
    revenue_high = any(x in r for x in ["250k", "500k", "1m", "1M"])
    revenue_mid = any(x in r for x in ["100k"])
    hours_high = any(x in h for x in ["60", "70", "80"])
    hours_low = any(x in h for x in ["20", "30", "40"])

    if revenue_high and hours_high:
        return "hot"
    elif revenue_high and not hours_low and not hours_high:
        return "qualified"
    elif revenue_mid and hours_high:
        return "qualified"
    elif revenue_high and hours_low:
        return "borderline"
    elif revenue_mid and hours_low:
        return "unqualified"
    else:
        return "unqualified"


def route_deals():
    tracker = load_json(TRACKER_PATH)
    leads = tracker.get("leads", [])
    results = []
    for lead in leads:
        revenue = lead.get("revenue", "")
        hours = lead.get("hours", "")
        tier = qualify(revenue, hours)
        result = {
            "name": lead.get("name", ""),
            "email": lead.get("email", ""),
            "revenue": revenue,
            "hours": hours,
            "tier": tier,
            "contact_id": lead.get("contact_id"),
            "opportunity_id": lead.get("opportunity_id"),
            "suggested_action": {
                "hot": "Send VIP email + SMS to David immediately",
                "qualified": "Send booking link via GHL workflow",
                "borderline": "Send qualification email + schedule follow-up",
                "unqualified": "Add to nurture sequence, no booking link",
            }[tier],
        }
        results.append(result)
    return results


if __name__ == "__main__":
    results = route_deals()
    print(f"Routed {len(results)} deals:")
    for r in results:
        print(f"  {r['name']:<20} | {r['revenue']:<12} | {r['hours']:<12} | {r['tier']:<12} | {r['suggested_action']}")
