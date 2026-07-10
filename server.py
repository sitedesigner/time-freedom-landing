#!/usr/bin/env python3
"""Time Freedom Landing Page - Form + Auth Tracking Server"""
import json
import http.server
import urllib.request
import urllib.error
import smtplib
import os
import ssl
import threading
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

    # Fallback: GHL blocks duplicates by unique fields; search existing contact and reuse it
    for field in ["email", "phone"]:
        value = data.get(field)
        if not value:
            continue
        try:
            search = ghl_request(
                "GET",
                f"/contacts/?locationId={LOCATION_ID}&{field}={urllib.parse.quote(value)}",
            )
            if isinstance(search, dict) and search.get("contacts"):
                return {"contact": search["contacts"][0]}
        except Exception:
            continue

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
        elif parsed.path == "/confirmation":
            self.serve_file("confirmation.html", "text/html")
        elif parsed.path == "/health":
            self.send_json(200, {"status": "ok"})
        elif parsed.path == "/api/ghl-status":
            self.handle_ghl_status()
        elif parsed.path == "/api/ghl-contact-test":
            self.handle_ghl_contact_test()
        elif parsed.path == "/api/1m-status":
            self.handle_1m_status()
        elif parsed.path == "/tracker-dashboard":
            self.serve_file("tracker-dashboard.html", "text/html")
        elif parsed.path == "/tracker/leads":
            self.handle_tracker_leads()
        else:
            self.send_error(404)

    def do_POST(self):
        parsed = urlparse(self.path)
        if parsed.path == "/api/submit":
            self.handle_submit()
        elif parsed.path == "/api/ghl-contact-test":
            self.handle_ghl_contact_test()
        elif parsed.path == "/api/book":
            self.handle_book()
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

    def handle_ghl_contact_test(self):
        if not GHL_TOKEN:
            self.send_json(400, {"success": False, "message": "GHL_TOKEN missing"})
            return

        # Read request body for optional test fields
        content_length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(content_length) if content_length else b""
        try:
            data = json.loads(body) if body else {}
        except json.JSONDecodeError:
            data = {}

        # Build a harmless test contact unless caller provides fields
        from datetime import datetime as _dt
        suffix = _dt.now().strftime("%Y%m%d%H%M%S")
        test_payload = {
            "firstName": data.get("firstName", "API"),
            "lastName": data.get("lastName", f"Test-{suffix}"),
            "email": data.get("email", f"ghl-api-test-{suffix}@example.com"),
            "phone": data.get("phone", f"555-01{suffix[-4:]}"),
            "locationId": LOCATION_ID,
            "tags": ["Time Freedom Landing Page", "Lead", "API-Test"],
        }
        revenue = data.get("revenue")
        hours = data.get("hours")
        if revenue:
            test_payload["tags"].append(f"Revenue:{revenue}")
        if hours:
            test_payload["tags"].append(f"Hours:{hours}")

        contact_result = create_contact(test_payload)
        if not contact_result or not contact_result.get("contact"):
            self.send_json(500, {
                "success": False,
                "message": "Contact creation failed",
                "raw": contact_result,
            })
            return

        contact = contact_result["contact"]
        contact_id = contact.get("id", "")

        # Try to create an opportunity in AGS Sales pipeline
        opp_result = ghl_request(
            "POST",
            "/opportunities/",
            {
                "name": f"Time Freedom Coaching - {contact.get('firstName', 'Test')} {contact.get('lastName', '')}",
                "status": "open",
                "contactId": contact_id,
                "locationId": LOCATION_ID,
                "pipelineId": PIPELINE_ID,
                "monetaryValue": 50000,
            },
        )

        self.send_json(200, {
            "success": True,
            "contact": contact,
            "opportunity": opp_result.get("opportunity") if opp_result else None,
            "raw_contact_response": contact_result,
            "raw_opportunity_response": opp_result,
        })

    def handle_1m_status(self):
        self.send_json(200, get_progress())

    def handle_tracker_leads(self):
        from tracker import load_tracker
        tracker = load_tracker()
        self.send_json(200, tracker)

    def handle_book(self):
        content_length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(content_length) if content_length else b""
        try:
            data = json.loads(body) if body else {}
        except json.JSONDecodeError:
            self.send_json(400, {"success": False, "message": "Invalid JSON"})
            return

        day = data.get("day", "").strip()
        time_block = data.get("time", "").strip()
        notes = data.get("notes", "").strip()
        if not day or not time_block:
            self.send_json(400, {"success": False, "message": "Day and time required"})
            return

        # Booking request received - update GHL and notify David
        booking_note = f"Booking request: {day} {time_block}. Notes: {notes or 'None'}"
        print(f"Booking request: {booking_note}")

        # Update opportunity with booking preference
        # This is best-effort; if it fails, we still return success to user
        try:
            from tracker import load_tracker, save_tracker
            tracker = load_tracker()
            leads = tracker.get("leads", [])
            if leads:
                last_lead = leads[-1]
                contact_id = last_lead.get("contact_id")
                opportunity_id = last_lead.get("opportunity_id")
                if contact_id and opportunity_id:
                    # Try to update opportunity with booking note
                    ghl_request("PUT", f"/opportunities/{opportunity_id}", {
                        "locationId": LOCATION_ID,
                        "notes": booking_note,
                    })
        except Exception as e:
            print(f"Booking GHL update error: {e}")

        # Send notification email to David
        try:
            email_body = f"New booking request: {day} {time_block}. Notes: {notes or 'None'}"
            send_welcome_email("David", GMAIL_USER)
            # Override the email content for booking notification
            import ssl
            from email.mime.text import MIMEText
            msg = MIMEText(f"Booking request received: {day} {time_block}. Notes: {notes or 'None'}")
            msg["Subject"] = "New Time Freedom Booking Request"
            msg["From"] = f"David Goecke <{GMAIL_USER}>"
            msg["To"] = GMAIL_USER
            context = ssl.create_default_context()
            with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
                server.login(GMAIL_USER, GMAIL_APP_PASSWORD)
                server.sendmail(GMAIL_USER, GMAIL_USER, msg.as_string())
        except Exception as e:
            print(f"Booking notification email error: {e}")

        self.send_json(200, {
            "success": True,
            "message": "Booking request sent. I'll reply within 24 hours with your Time Freedom Clarity Call link.",
            "booking": {"day": day, "time": time_block, "notes": notes},
        })

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

        # Respond to client immediately, then process integrations asynchronously
        self.send_json(200, {
            "success": True,
            "message": "Application submitted successfully",
            "contactId": "pending",
            "paymentLink": STRIPE_PAYMENT_LINK,
        })

        def process_async(payload=data):
            try:
                contact_result = create_contact(payload)
                contact_id = (contact_result or {}).get("contact", {}).get("id", "unknown")
                full_name = f"{payload.get('firstName', '')} {payload.get('lastName', '')}".strip()
                if contact_result and contact_result.get("contact"):
                    print(f"Contact created: {payload['email']} (ID: {contact_id})")
                else:
                    print(f"Contact failed or fallback failed for {payload['email']}")

                opp_result = create_opportunity(contact_id, full_name)
                opp_id = None
                if opp_result:
                    opp_id = opp_result.get("opportunity", {}).get("id", "unknown")
                    print(f"Opportunity created: {opp_id} ($50K)")

                send_welcome_email(payload["firstName"], payload["email"])
                add_lead(payload, contact_id=contact_id, opportunity_id=opp_id)
            except Exception as e:
                print(f"Async processing error: {e}")

        threading.Thread(target=process_async, daemon=True).start()

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
