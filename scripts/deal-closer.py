#!/usr/bin/env python3
"""Deal Closing Automation - builds summary, package, updates tracker with status"""
import json, os, re
from datetime import datetime
from pathlib import Path

BASE = Path(__file__).resolve().parent
DEALS_DIR = Path.home() / "Documents" / "GoTechSolutions" / "time-freedom-landing" / "deals"
TRACKER_PATH = Path.home() / "Documents" / "GoTechSolutions" / "time-freedom-landing" / "1m-tracker.json"


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
    slug = re.sub(r"[^a-z0-9]+", "-", (val or "").lower()).strip("-")
    return slug[:80] if slug else "deal"


def deal_stage(revenue, hours):
    r = (revenue or "").lower()
    h = (hours or "").lower()
    revenue_high = any(x in r for x in ["250k", "500k", "1m", "1M"])
    revenue_mid = any(x in r for x in ["100k", "100"])
    hours_high = any(x in h for x in ["60", "70", "80"])
    hours_mid = any(x in h for x in ["40", "50"])
    hours_low = any(x in h for x in ["20", "30"])
    if revenue_high and hours_high:
        return "Hot Lead - Book Now"
    if revenue_high and hours_mid:
        return "Qualified - Send Booking"
    if revenue_mid and hours_high:
        return "Qualified - Send Booking"
    if revenue_mid and hours_low:
        return "Nurture - No Booking"
    return "Review"


def build_deal_for_lead(lead):
    stage = deal_stage(lead.get("revenue"), lead.get("hours"))
    deal = {
        "deal_id": f"DEAL-{datetime.now().strftime('%Y%m%d-%H%M%S')}-{slugify(lead.get('name','lead'))}",
        "timestamp": datetime.now().isoformat(),
        "name": lead.get("name", ""),
        "email": lead.get("email", ""),
        "phone": lead.get("phone", ""),
        "revenue_range": lead.get("revenue", ""),
        "hours_range": lead.get("hours", ""),
        "challenge": lead.get("challenge", ""),
        "contact_id": lead.get("contact_id"),
        "opportunity_id": lead.get("opportunity_id"),
        "deal_value": lead.get("deal_value", 50000),
        "status": lead.get("status", "lead"),
        "stage": stage,
        "next_action": "Review application and send booking link" if "Book" in stage or "Qualified" in stage else "Add to nurture sequence",
        "notes": lead.get("notes", ""),
    }
    return deal


def save_deal_package(deal):
    DEALS_DIR.mkdir(parents=True, exist_ok=True)
    folder = DEALS_DIR / deal["deal_id"]
    folder.mkdir(parents=True, exist_ok=True)
    pkg = {
        "deal_id": deal["deal_id"],
        "lead_name": deal["name"],
        "email": deal["email"],
        "revenue": deal["revenue_range"],
        "hours": deal["hours_range"],
        "challenge": deal["challenge"],
        "contact_id": deal["contact_id"],
        "opportunity_id": deal["opportunity_id"],
        "deal_value": deal["deal_value"],
        "stage": deal["stage"],
        "next_action": deal["next_action"],
        "files": [],
        "created": datetime.now().isoformat(),
    }
    summaries = [f"""# Deal Summary: {deal['deal_id']}

## Lead
- Name: {deal['name']}
- Email: {deal['email']}
- Challenge: {deal['challenge']}

## Qualification
- Revenue Range: {deal['revenue_range'] or 'N/A'}
- Hours Worked: {deal['hours_range'] or 'N/A'}
- Deal Value: ${deal['deal_value']:,}

## GHL
- Contact ID: {deal['contact_id'] or 'N/A'}
- Opportunity ID: {deal['opportunity_id'] or 'N/A'}

## Recommended
- Stage: {deal['stage']}
- Next Action: {deal['next_action']}

Generated: {deal['timestamp']}
"""]
    notes = [f"""# Call Notes: {deal['name']}

Date: TBD

## Agenda
1. Review current revenue and hours
2. Identify leverage gaps
3. Present 90-day plan

## Outcomes


## Action Items


"""]
    plan = [f"""# 90-Day Execution Plan: {deal['name']}

## Phase 1: Foundation (Weeks 1-4)
- Audit current workflows
- Identify automation opportunities
- Setup AI tools

## Phase 2: Leverage (Weeks 5-8)
- Implement automations
- Delegate low-value tasks
- Optimize revenue streams

## Phase 3: Scale (Weeks 9-12)
- Review metrics
- Expand winning channels
- Build systems

## Milestones
- Week 4: Time saved = X hrs/week
- Week 8: Revenue increase = $X
- Week 12: Total time freedom = X hrs/week
"""]
    paths = []
    for name, content in [("deal-summary.md", summaries[0]), ("call-notes.md", notes[0]), ("90-day-plan.md", plan[0])]:
        p = folder / name
        p.write_text(content)
        paths.append(str(p))
    pkg["files"] = paths
    (folder / "package.json").write_text(json.dumps(pkg, indent=2))
    return pkg


def build_all_deals():
    tracker = load_json(TRACKER_PATH)
    leads = tracker.get("leads", [])
    packages = []
    for lead in leads:
        if not lead.get("email"):
            continue
        deal = build_deal_for_lead(lead)
        pkg = save_deal_package(deal)
        packages.append(pkg)
    return packages


def summary_for_deal(deal):
    return (
        f"DEAL: {deal['deal_id']}\n"
        f"NAME: {deal['name']}\n"
        f"EMAIL: {deal['email']}\n"
        f"VALUE: ${deal['deal_value']:,}\n"
        f"STAGE: {deal['stage']}\n"
        f"NEXT: {deal['next_action']}\n"
    )


if __name__ == "__main__":
    pkgs = build_all_deals()
    print(f"Built {len(pkgs)} deal packages")
    for p in pkgs:
        print(f"  {p['deal_id']} | {p['lead_name']} | ${p['deal_value']:,} | {p['stage']}")
        for f in p["files"]:
            print(f"    -> {f}")
