#!/usr/bin/env python3
"""Create calendar events for 2027 NY Challenge using .ics import."""
import json
import subprocess
import tempfile
import os
from datetime import datetime, timedelta

def make_ics(title, start_str, end_str, location, notes, uid=None):
    # Simple ICS format, dates as YYYYMMDDTHHMMSS
    dtstart = datetime.strptime(start_str, "%Y%m%d %H:%M:%S").strftime("%Y%m%dT%H%M%S")
    dtend = datetime.strptime(end_str, "%Y%m%d %H:%M:%S").strftime("%Y%m%dT%H%M%S")
    now = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
    uid = uid or f"{dtstart}-{title.replace(' ','')}@goetech"
    lines = [
        "BEGIN:VCALENDAR",
        "VERSION:2.0",
        "PRODID:-//GoTechSolutions//TimeFreedomChallenge//EN",
        "METHOD:PUBLISH",
        "BEGIN:VEVENT",
        f"UID:{uid}",
        f"DTSTAMP:{now}",
        f"DTSTART;VALUE=DATE-TIME:{dtstart}",
        f"DTEND;VALUE=DATE-TIME:{dtend}",
        f"SUMMARY:{title}",
        f"LOCATION:{location}",
        f"DESCRIPTION:{notes}",
        "END:VEVENT",
        "END:VCALENDAR",
    ]
    return "\r\n".join(lines) + "\r\n"

EVENTS = [
    ("2027 5-Day Time Freedom Reset - Day 1: Audit","20270104 09:00:00","20270104 10:30:00","Live via Zoom","Welcome, time audit framework, workbook walkthrough."),
    ("2027 5-Day Time Freedom Reset - Day 2: Elimination","20270105 09:00:00","20270105 10:30:00","Live via Zoom","Review audit, identify 10+ hours of waste, cutting plan."),
    ("2027 5-Day Time Freedom Reset - Day 3: Automation","20270106 09:00:00","20270106 10:30:00","Live via Zoom","One workflow you replace yourself in this week."),
    ("2027 5-Day Time Freedom Reset - Day 4: Leverage","20270107 09:00:00","20270107 10:30:00","Live via Zoom","Revenue per hour mapping. Align high-leverage activities."),
    ("2027 5-Day Time Freedom Reset - Day 5: Reset","20270108 09:00:00","20270108 11:00:00","Live via Zoom","90-day execution plan. Group accountability + pitch."),
    ("2027 Challenge - Prep Packet Ready","20261228 10:00:00","20261228 10:30:00","Email","Send prep workbook + private group invite to all signups."),
    ("2027 Challenge - First Promo Blast","20260716 12:00:00","20260716 12:30:00","LinkedIn / Email","First promo post. Link to /challenge. Start countdown."),
    ("2027 Challenge - Weekly LinkedIn Cadence","20260721 09:00:00","20260721 09:30:00","LinkedIn","Weekly reminder to register. Build urgency every Monday."),
    ("2027 Challenge - Sales Call Follow-up Day","20270111 09:00:00","20270111 17:00:00","Phone","Follow up with engaged challenge participants. Offer clarity calls."),
]

# Write all events to one combined ics file
ics_path = "/tmp/challenge_events.ics"
with open(ics_path, "w") as f:
    f.write("BEGIN:VCALENDAR\r\n")
    f.write("VERSION:2.0\r\n")
    f.write("PRODID:-//GoTechSolutions//TimeFreedomChallenge//EN\r\n")
    f.write("METHOD:PUBLISH\r\n")
    for i, ev in enumerate(EVENTS):
        title, s, e, loc, notes = ev
        dtstart = datetime.strptime(s, "%Y%m%d %H:%M:%S").strftime("%Y%m%dT%H%M%S")
        dtend = datetime.strptime(e, "%Y%m%d %H:%M:%S").strftime("%Y%m%dT%H%M%S")
        now = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
        uid = f"{dtstart}-challenge@goetech"
        f.write("BEGIN:VEVENT\r\n")
        f.write(f"UID:{uid}\r\n")
        f.write(f"DTSTAMP:{now}\r\n")
        f.write(f"DTSTART;VALUE=DATE-TIME:{dtstart}\r\n")
        f.write(f"DTEND;VALUE=DATE-TIME:{dtend}\r\n")
        f.write(f"SUMMARY:{title}\r\n")
        f.write(f"LOCATION:{loc}\r\n")
        f.write(f"DESCRIPTION:{notes}\r\n")
        f.write("END:VEVENT\r\n")
    f.write("END:VCALENDAR\r\n")

proc = subprocess.run(["open", ics_path], capture_output=True, text=True)
print("open exit:", proc.returncode)
print("stderr:", proc.stderr.strip())

with open("challenge_calendar_events.json", "w") as f:
    json.dump([{"title":e[0],"start":e[1],"end":e[2],"location":e[3],"notes":e[4]} for e in EVENTS], f, indent=2)
print("Saved challenge_calendar_events.json")
