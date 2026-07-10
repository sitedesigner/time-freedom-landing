#!/usr/bin/env python3
"""$1M Liquid Tracker - Updates automatically when leads come in"""
import json, os
from datetime import datetime

TRACKER_PATH = os.path.expanduser("~/Documents/GoTechSolutions/time-freedom-landing/1m-tracker.json")

def load_tracker():
    if os.path.exists(TRACKER_PATH):
        with open(TRACKER_PATH) as f:
            return json.load(f)
    return {
        "goal": 1000000,
        "started": datetime.now().isoformat(),
        "leads": [],
        "contacts_created": 0,
        "opportunities_created": 0,
        "emails_sent": 0,
        "deals_won": 0,
        "revenue_collected": 0,
        "pipeline_value": 0
    }

def save_tracker(tracker):
    os.makedirs(os.path.dirname(TRACKER_PATH), exist_ok=True)
    with open(TRACKER_PATH, "w") as f:
        json.dump(tracker, f, indent=2)

def add_lead(data, contact_id=None, opportunity_id=None):
    tracker = load_tracker()
    lead = {
        "timestamp": datetime.now().isoformat(),
        "name": f"{data.get('firstName', '')} {data.get('lastName', '')}".strip(),
        "email": data.get("email", ""),
        "phone": data.get("phone", ""),
        "company": data.get("company", ""),
        "revenue": data.get("revenue", ""),
        "hours": data.get("hours", ""),
        "challenge": data.get("challenge", ""),
        "contact_id": contact_id,
        "opportunity_id": opportunity_id,
        "deal_value": 50000
    }
    tracker["leads"].append(lead)
    tracker["contacts_created"] += 1
    tracker["emails_sent"] += 1
    if opportunity_id:
        tracker["opportunities_created"] += 1
        tracker["pipeline_value"] += 50000
    save_tracker(tracker)
    return tracker

def update_revenue(amount, contact_id=None):
    tracker = load_tracker()
    tracker["deals_won"] += 1
    tracker["revenue_collected"] += amount
    save_tracker(tracker)
    return tracker

def get_progress():
    tracker = load_tracker()
    collected_pct = (tracker["revenue_collected"] / tracker["goal"]) * 100
    pipeline_pct = (tracker["pipeline_value"] / tracker["goal"]) * 100
    total_pct = collected_pct + pipeline_pct
    
    return {
        "goal": tracker["goal"],
        "revenue_collected": tracker["revenue_collected"],
        "pipeline_value": tracker["pipeline_value"],
        "total_exposure": tracker["revenue_collected"] + tracker["pipeline_value"],
        "collected_pct": round(collected_pct, 2),
        "pipeline_pct": round(pipeline_pct, 2),
        "total_pct": round(total_pct, 2),
        "leads_count": len(tracker["leads"]),
        "contacts_created": tracker["contacts_created"],
        "opportunities_created": tracker["opportunities_created"],
        "deals_won": tracker["deals_won"]
    }

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "progress":
        print(json.dumps(get_progress(), indent=2))
    elif len(sys.argv) > 1 and sys.argv[1] == "revenue":
        amount = int(sys.argv[2])
        print(json.dumps(update_revenue(amount), indent=2))
    else:
        print(json.dumps(load_tracker(), indent=2))
