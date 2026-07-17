# 2027 5-Day Time Freedom Reset - GHL Campaign Setup

## What is already automated
- 19 GHL contacts tagged: 5-Day Challenge 2027, 5-Day Challenge 2027 Invited
- 12 LinkedIn social posts scheduled through Dec 2026
- Challenge landing page live: https://discerning-alignment-production-1b96.up.railway.app/challenge

## What to do in GHL UI (5 minutes)

### 1. Create Campaign
- Go to Marketing > Campaigns > Create Campaign
- Name: 2027 5-Day Time Freedom Reset
- Save

### 2. Add Email Sequence
Upload these 4 emails in order:
1. ghl-campaign/emails/01-welcome-invite.html (Day 0)
2. ghl-campaign/emails/02-day3-reminder.html (Day 3)
3. ghl-campaign/emails/03-day1-reminder.html (Day 6)
4. ghl-campaign/emails/04-final-call.html (Day 10)

For each: click Add Email > paste HTML > set delay in days > save

### 3. Create Automation
- Go to Automations > Create Workflow
- Trigger: Tag Added > 5-Day Challenge 2027
- Action 1: Add to Campaign > 2027 5-Day Time Freedom Reset
- Action 2: Add Tag > 5-Day Challenge 2027 Invited
- Save and turn ON

### 4. Connect Landing Page
In the challenge signup success flow (/api/challenge-signup), contacts are created in GHL with tag "5-Day Challenge 2027". The automation above will catch them and enroll them in the email sequence automatically.

## Next Actions
- Test a live signup at /challenge
- Verify contact appears in GHL with correct tags
- Verify automation enrolls them in campaign
