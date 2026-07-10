# GHL Qualification Workflow: Revenue + Hours Branching

## Goal
Only qualified leads receive a booking link. Unqualified leads go to nurture.

## Setup
- Location: y3al1fQwt4pfQXPocfh6
- Pipeline: AGS Sales mzb4UHFyaypa08ulsO6x ($50K default value)
- Tags applied by landing server:
  - Revenue:100k-250k
  - Revenue:250k-500k
  - Revenue:500k-1m
  - Hours:20-40
  - Hours:40-60
  - Hours:60-80
  - Lead
  - Time Freedom Landing Page

## Workflow 1: Qualified Lead (Revenue >= 250k AND Hours >= 40)

**Trigger:** Contact tag added AND matches any of:
- Revenue:250k-500k + Hours:40-60
- Revenue:250k-500k + Hours:60-80
- Revenue:500k-1m + Hours:40-60
- Revenue:500k-1m + Hours:60-80
- Revenue:100k-250k + Hours:60-80

**Actions:**
1. Wait: 6 hours
2. Send email: "Time Freedom Clarity Call - Let's lock your time"
3. Add tag: "Qualified - Booking Sent"
4. Update opportunity stage: "Appointment Booked" (or first stage if none)
5. Add note: "Booking link sent via workflow"
6. If email opened but no reply within 48 hours:
   - Send SMS reminder
   - Add tag: "Reminder Sent"
7. If link clicked:
   - Add tag: "Link Clicked"
   - Send notification to David (email/SMS)
8. If no activity after 7 days:
   - Move to nurture pipeline

## Workflow 2: High-Value Lead (Revenue >= 500k AND Hours >= 60)

**Trigger:** Contact tag added AND matches:
- Revenue:500k-1m + Hours:60-80

**Actions:**
1. Wait: 1 hour
2. Send SMS to David: "Hot lead on landing page: $500k-1M, 60-80hrs"
3. Send email: VIP priority response
4. Add tag: "Hot Lead - Personal Outreach"
5. Update opportunity stage: "Hot Lead"
6. Priority: Schedule call within 24 hours

## Workflow 3: Unqualified Lead (Revenue <= 100k OR Hours <= 40)

**Trigger:** Contact tag added AND matches:
- Revenue:100k-250k + Hours:20-40
- Revenue:100k-250k + Hours:40-60
- Any Revenue + Hours:20-40

**Actions:**
1. Wait: 12 hours
2. Send email: "Time Freedom podcast + content"
3. Add tag: "Nurture - Content"
4. Move to nurture pipeline
5. Do NOT send booking link
6. Re-evaluate in 90 days

## Workflow 4: Borderline Lead

**Trigger:** Does not match any of the above
- Revenue:100k-250k + Hours:60-80 (high hours, lower revenue)
- Revenue:250k-500k + Hours:20-40 (high revenue, low hours)

**Actions:**
1. Wait: 24 hours
2. Send email: "Is Time Freedom right for you right now?"
3. Add tag: "Borderline - Qualify First"
4. Update opportunity: add note with qualification questions
5. Schedule follow-up task for David

## Implementation Steps in GHL

1. Go to **Automation** > **Workflows**
2. Create 4 workflows as above
3. For each workflow:
   - Trigger: **Tag Added** (select matching tags)
   - Use **If/Else** branches for Revenue + Hours tag combinations
   - Use **Send Email** action with templates from `outreach-templates.md`
   - Use **Update Contact** to add qualification tags
   - Use **Update Opportunity** to change stage and add notes
4. Test each workflow with a test contact:
   - Add Revenue:500k-1m + Hours:60-80
   - Verify email sends and opportunity updates
5. Activate all workflows

## Timeline Rules
- Qualified: 6 hours wait before booking link
- High-Value: 1 hour wait, instant SMS
- Unqualified: 12 hours wait, no booking link
- Borderline: 24 hours wait, qualification email

## Email Templates
See: outreach-templates.md

## Monitoring
- Check GHL Workflow Runs daily
- Monitor tags: "Qualified", "Nurture", "Hot Lead"
- Review unqualified leads weekly for re-evaluation
