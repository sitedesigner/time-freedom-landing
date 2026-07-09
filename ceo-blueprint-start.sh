#!/bin/bash
# CEO Blueprint - Start Everything
# This starts the landing page server + tracker in one command

cd /Users/davidgo/time-freedom-landing

echo "========================================="
echo "  CEO BLUEPRINT - $1M Liquid System"
echo "========================================="
echo ""

# Load from .env
if [ -f .env ]; then
    export GHL_TOKEN=$(grep "^GHL_TOKEN=" .env | cut -d'=' -f2-)
    export LOCATION_ID=$(grep "^LOCATION_ID=" .env | cut -d'=' -f2-)
    export PIPELINE_ID=$(grep "^PIPELINE_ID=" .env | cut -d'=' -f2-)
    export GMAIL_USER=$(grep "^GMAIL_USER=" .env | cut -d'=' -f2-)
    export GMAIL_APP_PASSWORD=$(grep "^GMAIL_APP_PASSWORD=" .env | cut -d'=' -f2-)
fi

# Check required vars
if [ -z "$GHL_TOKEN" ] || [ -z "$GMAIL_APP_PASSWORD" ]; then
    echo "ERROR: Missing credentials in .env file"
    exit 1
fi

echo "Starting landing page server..."
echo "  Local: http://localhost:8080"
echo "  Health: http://localhost:8080/health"
echo "  GHL Status: http://localhost:8080/api/ghl-status"
echo "  1M Tracker: http://localhost:8080/api/1m-status"
echo ""
echo "Press Ctrl+C to stop"
echo "========================================="
echo ""

python3 server.py
