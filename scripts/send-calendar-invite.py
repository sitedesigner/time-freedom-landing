#!/usr/bin/env python3
"""Email .ics calendar invite to bizrunner@gmail.com."""
import os, json, smtplib, ssl
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders

ENV_PATH = "/Users/davidgo/Documents/GoTechSolutions/time-freedom-landing/.env"
cfg = {}
with open(ENV_PATH) as f:
    for line in f:
        line = line.strip()
        if line and "=" in line and not line.startswith("#"):
            k, v = line.split("=", 1)
            cfg[k.strip()] = v.strip()

user = cfg.get("GMAIL_USER", "")
pwd = cfg.get("GMAIL_APP_PASSWORD", "")
to = "bizrunner@gmail.com"

msg = MIMEMultipart()
msg["Subject"] = "2027 5-Day Time Freedom Reset - Calendar Events"
msg["From"] = f"David Goecke <{user}>"
msg["To"] = to
msg.attach(MIMEText("Hey David,\n\nAttached is the calendar file for the 2027 5-Day Time Freedom Reset and promo cadence. Import it into Google Calendar.\n\nTalk soon,\nDavid", "plain"))

ics_path = "/Users/davidgo/Documents/GoTechSolutions/time-freedom-landing/challenge_calendar_events.json"
with open(ics_path) as f:
    events = json.load(f)

# Build a simple ICS string
lines = ["BEGIN:VCALENDAR", "VERSION:2.0", "PRODID:-//GoTechSolutions//TimeFreedomChallenge//EN", "METHOD:REQUEST"]
for i, ev in enumerate(events):
    start = ev["start"].replace(" ", "T").replace(":", "")
    end = ev["end"].replace(" ", "T").replace(":", "")
    uid = f"{start}-challenge{i}@goetech"
    lines += [
        "BEGIN:VEVENT",
        f"UID:{uid}",
        f"DTSTART;VALUE=DATE-TIME:{start}",
        f"DTEND;VALUE=DATE-TIME:{end}",
        f"SUMMARY:{ev['title']}",
        f"LOCATION:{ev['location']}",
        f"DESCRIPTION:{ev['notes']}",
        "END:VEVENT",
    ]
lines.append("END:VCALENDAR")
ics = "\r\n".join(lines) + "\r\n"

part = MIMEBase("text", "calendar")
part.set_payload(ics)
encoders.encode_base64(part)
part.add_header("Content-Disposition", 'attachment; filename="challenge_events.ics"')
msg.attach(part)

context = ssl.create_default_context()
with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
    server.login(user, pwd)
    server.sendmail(user, to, msg.as_string())

print("Calendar invite sent to", to)
