# Agent: Gmail Syncer

## Context
Read before starting:
- `CLAUDE.md` — core rules, Notion Database ID
- `context/infrastructure.md` — Gmail status mapping table, Notion schema (Status field values), ambiguous email handling

Do NOT load: `context/profile.md`, `context/preferences.md`, `context/resume-format.md`

---

## Purpose
Check {{YOUR_EMAIL}} for emails from companies with applied roles. Map email signals to Notion status updates. Keep the tracker current without manual effort.

## Inputs
| Variable | Source |
|----------|--------|
| `{{LOOKBACK_DAYS}}` | Default 14 — check last 14 days of email |
| `{{DATE}}` | Current date |

## Steps

### Step 1 — Fetch applied roles from Notion
Query the Job Application Tracker database for rows where `Status` is one of: Applied, Confirmation Received, Interview Scheduled, Round 2, Round 3+.

Extract: company name, role title, date applied, current status, Notion page ID.

### Step 2 — Search Gmail for each company
For each applied company, use the Gmail MCP (`mcp__76387141-c378-4a16-afdc-52f4a6834bf4__search_threads`) with query:
```
from:{{COMPANY_DOMAIN}} after:{{DATE_MINUS_LOOKBACK}}
```

Also try searching by company name if domain is unknown:
```
{{COMPANY_NAME}} subject:(application OR interview OR offer OR decision OR next steps)
```

### Step 3 — Classify email signals
For each matching email thread, read the subject and first 500 chars of body. Classify:

| Signal | New Status |
|--------|-----------|
| "application received", "thank you for applying", "we've received your application" | Confirmation Received |
| "interview", "schedule a call", "speaking with you", "next step", "video call" | Interview Scheduled |
| "second round", "next round", "follow-up interview", "technical interview" | Round 2 |
| "third round", "final round", "final interview", "last stage" | Round 3+ |
| "offer", "pleased to offer", "compensation package", "congratulations" | Offer |
| "not moving forward", "other candidates", "decided not to proceed", "unfortunately", "regret to inform" | Rejected |
| "withdrawn", "no longer available", "position has been filled" | Withdrawn |

If unclear → do not update status. Log for manual review.

### Step 4 — Update Notion
For each confirmed status change:
1. Update the `Status` field in the database row
2. Add a note to the `Notes` field: "Status updated from [old] to [new] based on email received [date]. Subject: [subject line]"
3. If Interview Scheduled → add the interview date to Notes if it can be extracted from the email

### Step 5 — Report
Print a summary:
```
Gmail Sync — {{DATE}}
─────────────────────────────
✓ Confirmation Received:  Acme Corp (email {{DATE}})
✓ Interview Scheduled:    Example Inc (email {{DATE}}, {{DAY}} at {{TIME}})
→ No update:              Company A, Company B (no new emails)
─────────────────────────────
3 roles checked. 2 status updates applied.
```

## Rules
- Never update status backwards (e.g. Applied → Confirmation Received is forward; never move a role back to "To Apply")
- If an email is ambiguous, log it to `working/gmail_ambiguous_{{DATE}}.json` for manual review rather than guessing
- Do not mark Rejected unless the email is unambiguous. "We'll keep your profile on file" is NOT a rejection.
- If Gmail MCP is not connected → alert user: "Gmail MCP is not connected. Run /gmail-sync after connecting Gmail in Cowork settings."
