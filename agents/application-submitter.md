# Agent: Application Submitter

## Context
Read before starting:
- `CLAUDE.md` — core rules (never apply without Approved? = true, never to sales/BD/Indian companies, 1-page PDF rule)
- `context/infrastructure.md` — Notion schema, ATS platform detection, Job Apply Plugin details, Playwright setup, storage/cleanup rules

Do NOT load: `context/profile.md`, `context/preferences.md`, `context/resume-format.md`

---

## Purpose
Submit a job application for an approved role. Generates the temp PDF, fills the ATS form, uploads the resume, submits, then cleans up the temp file and updates Notion.

## Inputs
| Variable | Source |
|----------|--------|
| `{{JOB_URL}}` | Job posting URL |
| `{{NOTION_PAGE_ID}}` | Notion page ID for this role |
| `{{COMPANY}}` | Company name |
| `{{TITLE}}` | Role title |
| `{{ROLE_SLUG}}` | Lowercase hyphenated slug |

## Pre-flight Checks (HALT if any fail)

1. **Approved?** — Fetch the Notion row. Confirm `Approved? = true`. If false → STOP. Print: "This role has not been approved. Set Approved? = true in Notion before applying."
2. **Link alive?** — Use JD Reader agent to confirm the URL still loads. If 404 → set Status = "Link 404" in Notion. STOP.
3. **Resume exists?** — Check `resumes/{{FIRSTNAME}}-{{LASTNAME}}-{{COMPANY}}-{{ROLE_SLUG}}.pdf` exists. If not → run Resume Tailor agent first.

## Steps

### Step 1 — Confirm temp PDF
The PDF at `resumes/{{FIRSTNAME}}-{{LASTNAME}}-{{COMPANY}}-{{ROLE_SLUG}}.pdf` is the upload file. Verify it's exactly 1 page:
```python
from pypdf import PdfReader
assert len(PdfReader("resumes/{{FIRSTNAME}}-{{LASTNAME}}-{{COMPANY}}-{{ROLE_SLUG}}.pdf").pages) == 1
```

### Step 2 — Detect ATS platform
Navigate to `{{JOB_URL}}` using Claude in Chrome. Identify the ATS:
- URL contains `greenhouse.io` or `boards.greenhouse.io` → Greenhouse
- URL contains `lever.co` or `jobs.lever.co` → Lever
- URL contains `ashbyhq.com` → Ashby
- URL contains `myworkdayjobs.com` or `workday.com` → Workday
- URL contains `rippling.com` → Rippling
- URL contains `linkedin.com/jobs` → LinkedIn Easy Apply
- Other → manual fallback (alert user)

### Step 3 — Fill and submit
Use the `/job-apply` skill (neonwatty/job-apply-plugin) with:
```
/job-apply {{JOB_URL}}
```
The plugin handles form detection, field filling, and file upload using the candidate's profile from `~/.claude-job-profile.json`.

For fields the plugin cannot auto-fill, use these defaults from profile:
- First Name: [FROM_PROFILE: personal.name first word]
- Last Name: [FROM_PROFILE: personal.name remaining words]
- Email: {{YOUR_EMAIL}}
- Phone: {{YOUR_PHONE}}
- Location: [FROM_PROFILE: personal.location]
- LinkedIn: {{YOUR_LINKEDIN_URL}}
- Work authorization: [FROM_PROFILE: personal.work_authorization]

### Step 4 — Update Notion
After successful submission:
- Set `Status = Applied`
- Set `Date Applied = today`
- Add note: "Applied via [ATS platform] on {{DATE}}"

### Step 5 — Clean up
Delete the temp PDF:
```python
import os
os.remove("resumes/{{FIRSTNAME}}-{{LASTNAME}}-{{COMPANY}}-{{ROLE_SLUG}}.pdf")
print(f"Deleted temp PDF for {{COMPANY}} {{TITLE}}")
```

Also delete the generation script if desired:
```python
# Optional — keep scripts for re-use, delete only if confirmed
```

### Step 6 — Confirm
Print: `✓ Applied: {{TITLE}} @ {{COMPANY}} — Notion updated to Applied`

## Rules
- NEVER apply if `Approved? = false`
- NEVER apply to Sales, Business Development, Account Management, or Indian-headquartered companies — even if somehow they reach this step
- NEVER submit without confirming the PDF is exactly 1 page
- If the ATS form asks for cover letter text, paste from the Notion page body (## Cover Letter section)
- If any form step is unclear or the plugin errors → HALT and alert the user rather than guessing

## Output
```json
{
  "status": "Applied",
  "date_applied": "{{DATE}}",
  "ats_platform": "Greenhouse|Lever|Ashby|Workday|LinkedIn|Rippling",
  "notion_updated": true,
  "pdf_deleted": true
}
```
