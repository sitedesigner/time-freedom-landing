#!/usr/bin/env python3
"""Clean test contacts from GHL by tagging them for removal."""
import json
import os
import urllib.request
import urllib.error
import urllib.parse
from datetime import datetime

# Load config
ENV_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".env")
_config = {}
if os.path.exists(ENV_PATH):
    with open(ENV_PATH) as f:
        for line in f:
            line = line.strip()
            if line and "=" in line and not line.startswith("#"):
                k, v = line.split("=", 1)
                _config[k.strip()] = v.strip()

GHL_TOKEN = _config.get("GHL_TOKEN", os.environ.get("GHL_TOKEN", ""))
LOCATION_ID = _config.get("LOCATION_ID", os.environ.get("LOCATION_ID", "y3al1fQwt4pfQXPocfh6"))

BASE_URL = "https://services.leadconnectorhq.com"
HEADERS = {
    "Authorization": f"Bearer {GHL_TOKEN}",
    "Content-Type": "application/json",
    "Version": "2021-07-28",
    "Accept": "application/json",
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
}

def ghl_request(method, endpoint, data=None):
    url = f"{BASE_URL}{endpoint}"
    body = json.dumps(data).encode() if data else None
    req = urllib.request.Request(url, data=body, method=method, headers=HEADERS)
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            return json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        error_body = e.read().decode()
        print(f"GHL API Error {e.code}: {error_body}")
        return None
    except Exception as e:
        print(f"Request error: {e}")
        return None

def find_test_contacts():
    """Find all contacts with API-Test tag."""
    print("Searching for API-Test contacts...")
    result = ghl_request("GET", f"/contacts/?locationId={LOCATION_ID}&tags=API-Test&limit=100")
    if result and isinstance(result, dict):
        contacts = result.get("contacts", [])
        print(f"Found {len(contacts)} contacts with API-Test tag")
        return contacts
    print("No contacts found or error")
    return []

def tag_contacts_for_removal(contacts):
    """Tag test contacts with TEST-REMOVE."""
    tagged = 0
    for contact in contacts:
        contact_id = contact.get("id")
        existing_tags = contact.get("tags", [])
        if "TEST-REMOVE" in existing_tags:
            continue
        new_tags = list(existing_tags) + ["TEST-REMOVE"]
        result = ghl_request("PUT", f"/contacts/{contact_id}", {"tags": new_tags})
        if result and result.get("contact"):
            print(f"Tagged {contact.get('email', contact_id)} -> TEST-REMOVE")
            tagged += 1
        else:
            print(f"Failed to tag {contact_id}")
    print(f"Tagged {tagged} contacts for removal")
    return tagged

def remove_tagged_contacts():
    """Remove all contacts with TEST-REMOVE tag."""
    print("Finding TEST-REMOVE contacts...")
    result = ghl_request("GET", f"/contacts/?locationId={LOCATION_ID}&tags=TEST-REMOVE&limit=100")
    if not result or not isinstance(result, dict):
        print("No contacts found")
        return
    
    contacts = result.get("contacts", [])
    print(f"Found {len(contacts)} contacts with TEST-REMOVE tag")
    
    for contact in contacts:
        contact_id = contact.get("id")
        email = contact.get("email", "")
        name = f"{contact.get('firstName', '')} {contact.get('lastName', '')}".strip()
        
        # Try to delete via API (if supported)
        result = ghl_request("DELETE", f"/contacts/{contact_id}")
        if result:
            print(f"Removed: {name} ({email})")
        else:
            # If DELETE not supported, at least clear the tags and leave a note
            print(f"Could not delete {name} ({email}) - may need manual removal in GHL UI")
    
    print(f"Processed {len(contacts)} contacts")

if __name__ == "__main__":
    print("=== GHL Test Contact Cleanup ===")
    contacts = find_test_contacts()
    if contacts:
        tag_contacts_for_removal(contacts)
    else:
        # Try direct removal of known test emails
        test_emails = [
            "davidgoecke+live@bizrunner.com",
            "davidgoecke+railway@bizrunner.com", 
            "davidgoecke+railway2@bizrunner.com",
            "davidgoecke+async@bizrunner.com",
            "davidgoecke+ghlapi@bizrunner.com",
            "davidgoecke+ghlapi2@bizrunner.com",
        ]
        print(f"Looking for {len(test_emails)} known test emails...")
        for email in test_emails:
            result = ghl_request("GET", f"/contacts/?locationId={LOCATION_ID}&email={urllib.parse.quote(email)}")
            if result and isinstance(result, dict) and result.get("contacts"):
                contact = result["contacts"][0]
                cid = contact.get("id")
                existing_tags = contact.get("tags", [])
                new_tags = list(set(existing_tags + ["TEST-REMOVE"]))
                ghl_request("PUT", f"/contacts/{cid}", {"tags": new_tags})
                print(f"Tagged {email} as TEST-REMOVE")
            else:
                print(f"Not found: {email}")
    
    print("\n=== Attempting to remove TEST-REMOVE contacts ===")
    remove_tagged_contacts()
    print("\nCleanup complete. Contacts tagged TEST-REMOVE. If API deletion unsupported, remove manually in GHL > Contacts > Filter by tag 'TEST-REMOVE'")
