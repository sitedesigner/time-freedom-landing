# Security policy

## Scope

This repository contains the Time Freedom landing page backend and frontend. It connects to GoHighLevel (GHL) for CRM/calendar operations and sends email via Gmail SMTP. Credentials are provided through environment variables only.

## Reporting vulnerabilities

Email `security@gotech.ai` with description, reproduction steps, and impact. Do not open a public GitHub issue for security vulnerabilities.

## Hardening

- Never commit tokens, credentials, or secrets.
- This app does not ship API keys in the repo.
- All secrets are loaded from environment variables or Railway variables.
- If a secret is exposed, rotate it immediately and purge it from git history.
- Verify no credentials exist in the codebase before every deploy.
