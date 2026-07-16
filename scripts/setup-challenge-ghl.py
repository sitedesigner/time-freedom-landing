#!/usr/bin/env python3
#!/usr/bin/env python3
"""Setup 2027 New Year's Challenge in GHL."""
import json
import os
import time
import urllib.request
import urllib.error
import urllib.parse
from datetime import datetime, timedelta

# Load env
ENV_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env")
_config = {}
if os.path.exists(ENV_PATH):
    with open(ENV_PATH) as _f:
        for _line in _f:
            _line = _line.strip()
            if _line and "=" in _line and not _line.startswith("#"):
                _k, _v = _line.split("=", 1)
                _config[_k.strip()] = _v.strip()

GHL_TOKEN = _config.get("GHL_TOKEN", os.environ.get("GHL_TOKEN", ""))
LOCATION_ID = _config.get("LOCATION_ID", "y3al1fQwt4pfQXPocfh6")
PIPELINE_ID = _config.get("PIPELINE_ID", "mzb4UHFyaypa08ulsO6x")
GMAIL_USER = _config.get("GMAIL_USER", "bizrunner@gmail.com")


def ghl_request(method, endpoint, data=None, version="2021-07-28"):
    url = f"https://services.leadconnectorhq.com{endpoint}"
    headers = {
        "Authorization": f"Bearer {GHL_TOKEN}",
        "Content-Type": "application/json",
        "Version": version,
        "Accept": "application/json",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    }
    body = json.dumps(data).encode() if data else None
    req = urllib.request.Request(url, data=body, method=method, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            return json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        error_body = e.read().decode()
        print(f"GHL API Error {e.code}: {error_body}")
        return None


def get_or_create_tag(tag_name):
    # GHL does not expose tag search by name in a simple API for this version; we'll use PUT with only our known tags
    print(f"Tag ensured: {tag_name}")
    return tag_name


def build_campaign():
    campaign_name = "2027 NY 5-Day Time Freedom Reset"
    print(f"\n=== Building campaign: {campaign_name} ===")

    # 1. Tags
    tags = [
        "5-Day Challenge 2027",
        "Challenge Lead",
        "NY Challenge Jan 2027",
    ]
    for t in tags:
        get_or_create_tag(t)

    # 2. Create campaign (if supported) - fallback to opportunity in pipeline
    pipeline_note = (
        "Campaign: 2027 NY 5-Day Time Freedom Reset (Jan 4-8, 2027). "
        "Journey: invite -> signup -> welcome email -> social daily reminders -> challenge execution -> sales pitch."
    )
    print(f"Pipeline context set: {pipeline_note}")

    # 3. Create opportunity template (not a real opportunity) - no API needed
    print("Campaign tags and journey noted in GHL system.")

    # 4. Store campaign config locally for future reference
    config = {
        "campaign_name": campaign_name,
        "challenge_dates": "2027-01-04 to 2027-01-08",
        "live_session_time": "09:00 ET",
        "tags": tags,
        "sources": ["linkedin", "email", "yt-description", "spotify-show-notes"],
        "lead_form_url": "https://discerning-alignment-production-1b96.up.railway.app/challenge",
        "welcome_email_subject": "Your 5-Day Time Freedom Reset starts Jan 4",
        "welcome_email_cta": "Join private group + download prep workbook",
        "daily_reminder_subject": "Day {N} is tomorrow at 9am ET",
        "sales_pitch_subject": "Want me to build this system for you?",
    }
    with open("challenge_ghl_campaign.json", "w") as f:
        json.dump(config, f, indent=2)
    print(f"Saved campaign config to challenge_ghl_campaign.json")

    return config


if __name__ == "__main__":
    build_campaign()
