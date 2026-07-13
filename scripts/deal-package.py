#!/usr/bin/env python3
"""Deal Closing Package Builder"""
import json, os, re
from datetime import datetime
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent / "time-freedom-landing"
DEALS_DIR = BASE / "deals"

def slugify(val):
    slug = re.sub(r"[^a-z0-9]+", "-", (val or "").lower()).strip("-")
    return slug[:80] if slug else "lead"

def build_deal_package(lead):
    ts = datetime.now().strftime('%Y%m%d-%H%M%S')
    name = lead.get('name','Lead')
    email = lead.get('email','')
    revenue = lead.get('revenue','')
    hours = lead.get('hours','')
    challenge = lead.get('challenge','')
    contact_id = lead.get('contact_id')
    opportunity_id = lead.get('opportunity_id')
    deal_value = lead.get('deal_value', 50000)

    folder = DEALS_DIR / f"{slugify(name)}-{ts}"
    folder.mkdir(parents=True, exist_ok=True)

    # Summary markdown
    summary = folder / "deal-summary.md"
    summary.write_text(f"""# Deal Closing Package: {name}

## Lead
- Name: {name}
- Email: {email}
- Challenge: {challenge}

## Qualification
- Revenue: {revenue or 'N/A'}
- Hours: {hours or 'N/A'}
- Deal value: ${deal_value:,}

## GHL
- Contact ID: {contact_id or 'N/A'}
- Opportunity ID: {opportunity_id or 'N/A'}

## Recommended Offer
- Core offer: Time Freedom Coaching ${50_000}-${100_000}/yr

## Next Steps
1. Review application notes
2. Send booking link if qualified
3. 90-day execution plan
4. Close deal

Generated: {datetime.now().isoformat()}
""")

    # Notes file
    notes = folder / "call-notes.md"
    notes.write_text(f"""# Call Notes: {name}

## Date
TBD

## Attendees
- David Goecke
- {name}

## Agenda
1. Review current revenue and hours
2. Identify leverage gaps
3. Present 90-day plan

## Outcomes


## Action Items


""")

    # 90-day plan template
    plan = folder / "90-day-plan.md"
    plan.write_text(f"""# 90-Day Execution Plan: {name}

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

""")

    package = {
        "deal_id": folder.name,
        "lead_name": name,
        "email": email,
        "deal_value": deal_value,
        "files": [str(summary), str(notes), str(plan)],
        "created": datetime.now().isoformat(),
    }
    (folder / "package.json").write_text(json.dumps(package, indent=2))
    return package

if __name__ == '__main__':
    # Build packages for all leads in tracker
    tracker_path = BASE / "1m-tracker.json"
    tracker = json.loads(tracker_path.read_text()) if tracker_path.exists() else {"leads":[]}
    leads = tracker.get('leads', [])
    if not leads:
        print('No leads found in tracker')
    else:
        packages = []
        for lead in leads:
            pkg = build_deal_package(lead)
            packages.append(pkg)
            print(f"Built package: {pkg['deal_id']} -> {pkg['files']}")
        print(f'\nTotal packages: {len(packages)}')
