#!/bin/bash
cd /Users/davidgo/time-freedom-landing
kill $(lsof -ti:8080) 2>/dev/null
export GHL_TOKEN="pit-...45b0"
export PIPELINE_ID="mzb4UHFyaypa08ulsO6x"
export GMAIL_USER="bizrunner@gmail.com"
export GMAIL_APP_PASSWORD="REPLACE_WITH_GMAIL_APP_PASSWORD"
nohup python3 server.py > /tmp/tf-server.log 2>&1 &
sleep 3
