#!/usr/bin/env python3
"""Time Freedom Landing Page - Form + Auth Tracking Server"""
import json
import http.server
import urllib.request
import urllib.error
import smtplib
import os
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from urllib.parse import urlparse
from tracker import add_lead, get_progress


# Config - primary source is .env file in the same directory
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
LOCATION_ID = _config.get("LOCATION_ID", os.environ.get("LOCATION_ID", "y3al1fQwt4pfQXPocfh6"))
PIPELINE_ID = _config.get("PIPELINE_ID", os.environ.get("PIPELINE_ID", "mzb4UHFyaypa08ulsO6x"))
PORT = int(os.environ.get("PORT", "8080"))
GMAIL_USER = _config.get("GMAIL_USER", os.environ.get("GMAIL_USER", "bizrunner@gmail.com"))
GMAIL_APP_PASSWORD = _config.get("GMAIL_APP_PASSWORD", os.environ.get("GMAIL_APP_PASSWORD", ""))
STRIPE_PAYMENT_LINK = _config.get("STRIPE_PAYMENT_LINK", os.environ.get("STRIPE_PAYMENT_LINK", ""))


def ghl_request(method, endpoint, data=None):
    url = f"https://services.leadconnectorhq.com{endpoint}"
    headers = {
        "Authorization": f"Bearer {GHL_TOKEN}",
        "Content-Type": "application/json",
        "Version": "2021-07-28",
        "Accept": "application/json",
        "User-Agent": "TimeFreedom-Landing/1.0",
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


def create_contact(data):
    revenue = data.get("revenue", "")
    hours = data.get("hours", "")
    payload = {
        "firstName": data.get("firstName", ""),
        "lastName": data.get("lastName", ""),
        "email": data.get("email", ""),
        "phone": data.get("phone", ""),
        "locationId": LOCATION_ID,
        "tags": ["Time Freedom Landing Page", "Lead"],
    }
    if revenue:
        payload["tags"].append(f"Revenue:{revenue}")
    if hours:
        payload["tags"].append(f"Hours:{hours}")

    result = ghl_request("POST", "/contacts/", payload)
    if result and result.get("contact"):
        return result

    # Fallback: search by email/phone and reuse existing contact instead of failing on duplicate
    for field in ["email", "phone"]:
        value = data.get(field)
        if not value:
            continue
        search = ghl_request(
            "GET",
            f"/contacts/?locationId={LOCATION_ID}&{field}={urllib.parse.quote(value)}",
        )
        if isinstance(search, dict) and search.get("contacts"):
            contact = search["contacts"][0]
            return {"contact": contact}

    return result


def create_opportunity(contact_id, full_name):
    return ghl_request(
        "POST",
        "/opportunities/",
        {
            "name": f"Time Freedom Coaching - {full_name}",
            "status": "open",
            "contactId": contact_id,
            "locationId": LOCATION_ID,
            "pipelineId": PIPELINE_ID,
            "monetaryValue": 50000,
        },
    )


def send_welcome_email(first_name, email):
    try:
        text = f"Hey {first_name},\n\nThanks for applying to work with me on Time Freedom.\n\nI'll review your application within 24 hours. If we're a fit, I'll send you a link to book a free strategy call.\n\nTalk soon,\nDavid Goecke\n425-466-8650"

        html = f"""<!DOCTYPE html>
<html>
<body style="font-family: system-ui, sans-serif; background:#0a0a0a; color:#fff; padding:40px 20px;">
  <div style="max-width:500px; margin:0 auto;">
    <p style="color:#a855f7; font-size:12px; letter-spacing:3px; text-transform:uppercase; font-weight:700;">David Goecke</p>
    <h1 style="font-size:24px; font-weight:800; margin-bottom:12px;">Hey {first_name}, your time freedom starts now.</h1>
    <p style="color:#a0a0a0; line-height:1.6; margin-bottom:24px;">Thanks for applying to work with me on Time Freedom.</p>
    <p style="color:#a0a0a0; line-height:1.6; margin-bottom:24px;">No fluff. No BS. Just results.</p>
    <p style="color:#666; font-size:14px;">Talk soon,<br><strong style="color:#fff;">David Goecke</strong><br><a href="tel:4254668650" style="color:#a855f7;">425-466-8650</a></p>
  </div>
</body>
</html>"""

        msg = MIMEMultipart("alternative")
        msg["Subject"] = f"{first_name}, your time freedom starts now"
        msg["From"] = f"David Goecke <{GMAIL_USER}>"
        msg["To"] = email
        msg.attach(MIMEText(text, "plain"))
        msg.attach(MIMEText(html, "html"))

        context = ssl.create_default_context()
        with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
            server.login(GMAIL_USER, GMAIL_APP_PASSWORD)
            server.sendmail(GMAIL_USER, email, msg.as_string())
        print(f"Welcome email sent to {email}")
    except Exception as e:
        print(f"Email error: {e}")


class Handler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        parsed = urlparse(self.path)
        if parsed.path == "/":
            self.serve_file("index.html", "text/html")
        elif parsed.path == "/deal-room":
            self.serve_file("deal-room.html", "text/html")
        elif parsed.path == "/health":
            self.send_json(200, {"status": "ok"})
        elif parsed.path == "/api/ghl-status":
            self.handle_ghl_status()
        elif parsed.path == "/api/1m-status":
            self.handle_1m_status()
        else:
            self.send_error(404)

    def do_POST(self):
        parsed = urlparse(self.path)
        if parsed.path == "/api/submit":
            self.handle_submit()
        else:
            self.send_error(404)

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def handle_ghl_status(self):
        auth_info = {
            "token_present": bool(GHL_TOKEN),
            "token_prefix": GHL_TOKEN[:8] if GHL_TOKEN else "",
            "location_id": LOCATION_ID,
            "pipeline_id": PIPELINE_ID,
            "contact_api": "unknown",
            "opportunity_api": "unknown",
            "location_api": "unknown",
        }
        if not GHL_TOKEN:
            self.send_json(200, auth_info)
            return

        loc = ghl_request("GET", f"/locations/{LOCATION_ID}")
        auth_info["location_api"] = "ok" if loc is not None else "error"
        auth_info["location_name"] = (loc or {}).get("name", "")
        auth_info["traceId"] = (loc or {}).get("traceId", "") if isinstance(loc, dict) else ""

        # Do not create real test data here, so /api/ghl-status stays side-effect free.
        self.send_json(200, auth_info)

    def handle_1m_status(self):
        self.send_json(200, get_progress())

    def handle_submit(self):
        content_length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(content_length)
        try:
            data = json.loads(body)
        except json.JSONDecodeError:
            self.send_json(400, {"success": False, "message": "Invalid JSON"})
            return

        if not data.get("firstName") or not data.get("email"):
            self.send_json(400, {"success": False, "message": "Name and email required"})
            return

        contact_result = create_contact(data)
        if not contact_result:
            self.send_json(500, {"success": False, "message": "Failed to create contact"})
            return

        contact_id = contact_result.get("contact", {}).get("id", "unknown")
        full_name = f"{data.get('firstName', '')} {data.get('lastName', '')}".strip()
        print(f"Contact created: {data['email']} (ID: {contact_id})")

        opp_result = create_opportunity(contact_id, full_name)
        opp_id = None
        if opp_result:
            opp_id = opp_result.get("opportunity", {}).get("id", "unknown")
            print(f"Opportunity created: {opp_id} ($50K)")

        send_welcome_email(data["firstName"], data["email"])
        add_lead(data, contact_id=contact_id, opportunity_id=opp_id)

        self.send_json(
            200,
            {
                "success": True,
                "message": "Application submitted successfully",
                "contactId": contact_id,
                "paymentLink": STRIPE_PAYMENT_LINK,
            },
        )

    def serve_file(self, filename, content_type):
        filepath = os.path.join(os.path.dirname(os.path.abspath(__file__)), filename)
        try:
            with open(filepath, "rb") as f:
                content = f.read()
            self.send_response(200)
            self.send_header("Content-Type", content_type)
            self.send_header("Content-Length", len(content))
            self.end_headers()
            self.wfile.write(content)
        except FileNotFoundError:
            self.send_error(404)

    def send_json(self, status, data):
        body = json.dumps(data).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Content-Length", len(body))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, format, *args):
        pass


if __name__ == "__main__":
    print(f"Time Freedom Landing Page running on port {PORT}")
    print(f"Health: http://localhost:{PORT}/health")
    print(f"GHL auth status: http://localhost:{PORT}/api/ghl-status")
    server = http.server.HTTPServer(("0.0.0.0", PORT), Handler)
    server.serve_forever()
