# Calendly Qualification Workflow for GHL

## Goal
Only qualified leads (based on revenue + hours) receive a Calendly booking link. Everyone else goes to a nurture sequence.

## Step 1: Create Custom Fields in GHL
These will be used for branching logic.

Fields:
- Name: `Revenue Range`
  Type: dropdown
  Options: 50k-100k, 100k-250k, 250k-500k, 500k-1m, 1m+

- Name: `Hours Worked`
  Type: dropdown
  Options: under40, 40-50, 50-60, 60-80, 80+

Already captured by landing page form and sent as tags.

## Step 2: Trigger in GHL
When a contact is created via the landing page API, the tags come in as:
- Revenue:250k-500k
- Hours:60-80

## Step 3: Branching Logic

### High-Value Leads (send Calendly link immediately):
- Revenue >= $100K/mo AND Hours >= 50/week
Tags example: Revenue:100k-250k or higher combined with Hours:50-60 or higher

Action: Send SMS/email with Calendly link
Wait: 0 hours
Then: If no booking in 48 hours, send reminder

### Qualify But Not Ready (nurture):
- Revenue >= $100K/mo but Hours < 50/week
  OR
- Revenue between 50k-100k with Hours >= 50/week

Action: Send email nurture sequence
Sequence: 3 emails over 7 days
Content: Time Freedom case studies, leverage frameworks, David's YouTube clips

### Not Qualified Yet (long-term nurture):
- Revenue below $50K/mo OR Hours under 40/week

Action: Add to YouTube subscriber nurture
No Calendly link

## Step 4: Calendly Questions to Match
The confirmation page already asks 3 questions. Make sure Calendly invite asks:
1. What is your current monthly revenue?
2. How many hours/week do you work?
3. What is your #1 leverage gap right now?

## Step 5: Post-Booking
When booking confirmed in Calendly:
1. Update GHL contact status to "Meeting Booked"
2. Update opportunity stage to "Appointment Booked"
3. Send confirmation email with Zoom link
4. Add reminder tasks in GHL:
   - 24 hours before: SMS reminder
   - 1 hour before: Email reminder with Zoom link

## Step 6: Post-Call
If call completed:
1. Update opportunity stage to "Presentation"
2. Send proposal within 2 hours
3. If no-show: send 3-day follow-up sequence to reschedule

## Implementation Notes
- Landing page already pipes tags into GHL
- Need to add Calendly webhook handler in server.py OR use native GHL workflow automation
- Prefer GHL native workflows because it bypasses Railway SMTP restrictions
- Calendly webhook endpoint: /api/calendly-webhook

## Revenue Thresholds
Immediate booking: $100K+ revenue and 50+ hours
Nurture: under thresholds but showing intent
Long-term: not yet at threshold
