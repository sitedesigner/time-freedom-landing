#!/usr/bin/env python3
"""Generate social planner posts for 2027 NY Challenge - future dates only."""
import json
import os
from datetime import datetime, timedelta

BASE_DATE = datetime(2026, 7, 16)
CHALLENGE_START = datetime(2027, 1, 4)

def days_until():
    return (CHALLENGE_START - BASE_DATE).days

POSTS = [
    {
        "when": BASE_DATE + timedelta(days=1, hours=9),
        "body": "Big move: I am opening 50 seats for the 5-Day Time Freedom Reset Jan 4-8, 2027.\n\nFive days. Real work. No fluff.\nDay 1: Time Audit. Day 2: Elimination. Day 3: Automation. Day 4: Leverage. Day 5: Reset.\n\nIf you are doing good work but drowning in execution, this is your off ramp.\n\nApply now: https://discerning-alignment-production-1b96.up.railway.app/challenge\n\n#TimeFreedom #AI #Faith #Coaching"
    },
    {
        "when": BASE_DATE + timedelta(days=8, hours=9),
        "body": f"One week closer to the 5-Day Time Freedom Reset ({days_until() - 8} days out).\n\nThe fastest way to reclaim your time is to stop adding tasks and start removing them.\n\nDay 2 of the challenge is Elimination. That is where the real hours come back.\n\nReserve your spot: https://discerning-alignment-production-1b96.up.railway.app/challenge\n\n#TimeFreedom #Leverage"
    },
    {
        "when": BASE_DATE + timedelta(days=15, hours=9),
        "body": f"{days_until() - 15} days until the 5-Day Time Freedom Reset kicks off.\n\nMost coaches and operators do not have a revenue problem. They have an attention problem.\n\nThe challenge fixes that in 5 days.\n\nApply now: https://discerning-alignment-production-1b96.up.railway.app/challenge\n\n#AI #Faith #Coaching"
    },
    {
        "when": BASE_DATE + timedelta(days=30, hours=9),
        "body": f"{days_until() - 30} days out.\n\nI built this challenge because I was working 80-hour weeks and still missing the mark on revenue.\n\n90 days after applying the reset, I hit $50K-$100K without losing my weekends.\n\nYour turn. Jan 4-8.\n\nSign up: https://discerning-alignment-production-1b96.up.railway.app/challenge"
    },
    {
        "when": BASE_DATE + timedelta(days=60, hours=9),
        "body": f"60 days until Jan 4.\n\nThe 5-Day Time Freedom Reset is not a webinar series. It is a work sprint.\n\nYou will leave with a 90-day execution plan and one workflow that runs without you.\n\nLimited seats. Apply now: https://discerning-alignment-production-1b96.up.railway.app/challenge\n\n#TimeFreedom"
    },
    {
        "when": BASE_DATE + timedelta(days=90, hours=9),
        "body": "90 days to go.\n\nI am looking for 50 people who want to start 2027 with a system.\n\nIf that is you, do not wait. Seats are limited by design.\n\nApply: https://discerning-alignment-production-1b96.up.railway.app/challenge"
    },
    {
        "when": BASE_DATE + timedelta(days=120, hours=9),
        "body": f"120 days until the 5-Day Time Freedom Reset.\n\nApply here: https://discerning-alignment-production-1b96.up.railway.app/challenge"
    },
    {
        "when": BASE_DATE + timedelta(days=150, hours=9),
        "body": "If you are reading this in July 2026, you are early.\n\nEarly means you get first access and the biggest seat.\n\n5-Day Time Freedom Reset. Jan 4-8, 2027.\n\nApply: https://discerning-alignment-production-1b96.up.railway.app/challenge"
    },
    {
        "when": BASE_DATE + timedelta(days=180, hours=9),
        "body": "Almost half a year out and seats are already moving.\n\nDo not wait for the reminder texts. Claim your spot now.\n\nhttps://discerning-alignment-production-1b96.up.railway.app/challenge"
    },
    {
        "when": datetime(2026, 12, 1, 9, 0),
        "body": "December is here. The 5-Day Time Freedom Reset starts in 34 days.\n\n2026 is almost over. Start 2027 on your terms.\n\nApply: https://discerning-alignment-production-1b96.up.railway.app/challenge"
    },
    {
        "when": datetime(2026, 12, 15, 9, 0),
        "body": "19 days left.\n\nFinal seat block just opened.\n\nDo not start January still doing 2026's hustle.\n\nRegister now: https://discerning-alignment-production-1b96.up.railway.app/challenge"
    },
    {
        "when": datetime(2026, 12, 28, 9, 0),
        "body": "One week out.\n\nYour prep workbook is in your inbox. Check it before Monday.\n\n5-Day Time Freedom Reset starts Jan 4. Live at 9am ET.\n\nSee you inside.\n\nhttps://discerning-alignment-production-1b96.up.railway.app/challenge"
    },
]

output = []
for p in POSTS:
    output.append({
        "accountIds": ["6a42b4933d60d412ea965d07_y3al1fQwt4pfQXPocfh6_xV3wsjivin_profile"],
        "summary": p["body"],
        "media": [],
        "status": "scheduled",
        "scheduleDate": p["when"].strftime("%Y-%m-%dT%H:%M:%S-04:00"),
        "type": "post",
        "userId": "system",
    })

with open("challenge_social_posts.json", "w") as f:
    json.dump(output, f, indent=2)
print(f"Generated {len(output)} social posts -> challenge_social_posts.json")
