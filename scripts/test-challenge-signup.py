#!/usr/bin/env python3
"""Test challenge signup with a fixed email to verify GHL flow."""
import json, os, urllib.request, urllib.error

ENV_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".env")
cfg={}
with open(ENV_PATH) as f:
    for line in f:
        line=line.strip()
        if line and "=" in line and not line.startswith("#"):
            k,v=line.split("=",1); cfg[k.strip()]=v.strip()

url="https://discerning-alignment-production-1b96.up.railway.app/api/challenge-signup"
data=json.dumps({
    "firstName": "Zuna",
    "lastName": "Hercules",
    "email": "zuna-hercules-test@example.com",
    "phone": "425-466-8650",
    "revenue": "100k-250k",
    "hours": "50-60",
    "goal": "Hercules mode test"
}).encode()
headers={"Content-Type": "application/json"}
req=urllib.request.Request(url, data=data, headers=headers, method="POST")
try:
    with urllib.request.urlopen(req, timeout=15) as r:
        print(r.status, json.loads(r.read().decode()))
except urllib.error.HTTPError as e:
    print(e.code, e.read().decode())
