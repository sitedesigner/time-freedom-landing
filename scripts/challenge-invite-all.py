#!/usr/bin/env python3
"""Tag all existing GHL contacts with the 2027 NY Challenge invite tag."""
import json, os, urllib.request, urllib.error, time

ENV_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".env")
_config = {}
with open(ENV_PATH) as f:
    for line in f:
        line = line.strip()
        if line and "=" in line and not line.startswith("#"):
            k, v = line.split("=", 1)
            _config[k.strip()] = v.strip()

TOKEN=_config.get("GHL_TOKEN", os.environ.get("GHL_TOKEN", ""))
LOCATION_ID = _config.get("LOCATION_ID", "y3al1fQwt4pfQXPocfh6")
BASE = "https://services.leadconnectorhq.com"
HEADERS = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json",
    "Version": "2021-07-28",
    "Accept": "application/json",
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
}

INVITE_TAG = "5-Day Challenge 2027 Invited"
CHALLENGE_TAG = "5-Day Challenge 2027"

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

def tag_all_contacts():
    data = ghl("GET", f"/contacts/?locationId={LOCATION_ID}")
    if not data or not data.get("contacts"):
        print("No contacts found")
        return
    contacts = data["contacts"]
    tagged = 0
    for c in contacts:
        cid = c.get("id", "")
        tags = list(set(c.get("tags", []) + [CHALLENGE_TAG, INVITE_TAG]))
        ghl("PUT", f"/contacts/{cid}", {"tags": tags})
        tagged += 1
        time.sleep(0.3)
    print(f"Done. Tagged {tagged} contacts with challenge invite tags.")
    with open("challenge_invite_log.json", "w") as f:
        json.dump({"tagged": tagged}, f)

if __name__ == "__main__":
    tag_all_contacts()
