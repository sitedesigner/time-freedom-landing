#!/usr/bin/env python3
"""Upload one challenge social post to GHL."""
import json
import os
import sys
import urllib.request
import urllib.error

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
ACCOUNT_ID = "6a42b4933d60d412ea965d07_y3al1fQwt4pfQXPocfh6_xV3wsjivin_profile"

BASE_URL = "https://services.leadconnectorhq.com"
HEADERS = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json",
    "Version": "v3",
    "Accept": "application/json",
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
}

POSTS_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "challenge_social_posts.json")

with open(POSTS_PATH) as f:
    posts = json.load(f)

idx = int(sys.argv[1]) if len(sys.argv) > 1 else 0
if idx >= len(posts):
    print(f"No post at index {idx}")
    sys.exit(1)

post = posts[idx]
post["accountIds"] = [ACCOUNT_ID]
post["userId"] = "system"

url = f"{BASE_URL}/social-media-posting/{LOCATION_ID}/posts"
req = urllib.request.Request(url, data=json.dumps(post).encode(), headers=HEADERS, method="POST")
try:
    with urllib.request.urlopen(req, timeout=30) as resp:
        result = json.loads(resp.read().decode())
        print(json.dumps({"index": idx, "status": "created", "result": result}, indent=2))
except urllib.error.HTTPError as e:
    body = e.read().decode()
    print(f"Error {e.code}: {body}")
    with open("challenge_social_errors.log", "a") as f:
        f.write(f"index={idx} code={e.code} body={body}\n")
