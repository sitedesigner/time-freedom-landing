#!/usr/bin/env python3
"""Build 2027 Challenge GHL campaign, email sequence, and automation."""
import json, os, urllib.request, urllib.error, time

ENV_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".env")
_config = {}
with open(ENV_PATH) as f:
    for line in f:
        line = line.strip()
        if line and "=" in line and not line.startswith("#"):
            k, v = line.split("=", 1)
            _config[k.strip()] = v.strip()

TOKEN = _config.get("GHL_TOKEN", os.environ.get("GHL_TOKEN", ""))
LOCATION_ID = _config.get("LOCATION_ID", "y3al1fQwt4pfQXPocfh6")
BASE = "https://services.leadconnectorhq.com"
HEADERS = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json",
    "Version": "2021-07-28",
    "Accept": "application/json",
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
}

def ghl(method, endpoint, data=None):
    req = urllib.request.Request(
        f"{BASE}{endpoint}",
        data=json.dumps(data).encode() if data else None,
        headers=HEADERS,
        method=method,
    )
    try:
        with urllib.request.urlopen(req, timeout=15) as r:
            return json.loads(r.read().decode())
    except urllib.error.HTTPError as e:
        body = e.read().decode()
        print(f"GHL {method} {endpoint} -> {e.code}: {body}")
        return None

def build():
    # 1. Create campaign
    print("Creating campaign...")
    camp = ghl("POST", "/campaigns/", {"name": "2027 5-Day Time Freedom Reset", "locationId": LOCATION_ID})
    if not camp:
        print("Campaign creation failed.")
        return
    camp_id = camp.get("id") or camp.get("_id")
    print(f"Campaign ID: {camp_id}")
    time.sleep(1)

    # 2. Create email sequence
    emails = [
        ("Welcome + Invite", "You are invited. 5-Day Time Freedom Reset Jan 4-8", 0),
        ("Day 3 Reminder", "3 days until the Time Freedom Reset", 3),
        ("Day 1 Reminder", "Tomorrow we start. 5-Day Time Freedom Reset", 6),
        ("Final Call", "Last chance to join", 10),
    ]
    for name, subject, delay in emails:
        html = f"""<!DOCTYPE html>
<html><body style="font-family: system-ui, sans-serif; background:#0a0a0a; color:#fff; padding:40px 20px;">
  <div style="max-width:500px; margin:0 auto;">
    <p style="color:#a855f7; font-size:12px; letter-spacing:3px; text-transform:uppercase; font-weight:700;">AI + Faith</p>
    <h1 style="font-size:24px; font-weight:800; margin-bottom:12px;">{name}</h1>
    <p style="color:#a0a0a0; line-height:1.6; margin-bottom:24px;">5-Day Time Freedom Reset starts Jan 4, 2027. Daily at 9am ET.</p>
    <p style="color:#a0a0a0; line-height:1.6; margin-bottom:24px;"><a href="https://discerning-alignment-production-1b96.up.railway.app/challenge" style="color:#a855f7;">Claim your spot</a></p>
  </div>
</body></html>"""
        print(f"Creating email: {name}")
        ghl("POST", "/campaigns/emails/", {
            "campaignId": camp_id,
            "name": name,
            "subject": subject,
            "htmlBody": html,
            "textBody": "Plain text fallback",
            "delay": {"type": "days", "value": delay},
            "locationId": LOCATION_ID,
        })
        time.sleep(1)

    # 3. Create automation
    print("Creating automation...")
    ghl("POST", "/automations/", {
        "name": "2027 Challenge - Invite to Campaign",
        "locationId": LOCATION_ID,
        "triggerType": "tagAdded",
        "actions": [
            {"type": "addToCampaign", "campaignId": camp_id},
            {"type": "addTag", "tag": "5-Day Challenge 2027"},
        ],
    })
    print("Campaign build complete.")

if __name__ == "__main__":
    build()
