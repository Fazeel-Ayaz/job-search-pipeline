# Job Search Infrastructure
> Loaded by: Notion Logger, Gmail Syncer
> Also useful for: any agent that writes to or reads from Notion
> Do NOT load for: Resume Tailor, Cover Letter Writer, Role Scorer, ATS Scanner, Legitimacy Check

---

## Notion Tracker

> IDs are read from `claude-job-profile.json` in the project root. Never hardcode them here.

- **Tracker Page:** `notion.job_search_page_url` from profile
- **Database URL:** `notion.tracker_database_url` from profile
- **Database ID:** `notion.database_id` from profile
- **Parent Page ID:** `notion.parent_page_id` from profile
- **Data Source ID:** `notion.data_source_id` from profile

### Schema Columns

| Field | Type | Notes |
|-------|------|-------|
| `Role Title` | title | |
| `Company` | text | |
| `Location` | text | |
| `Status` | select | To Apply → Applied → Confirmation Received → Interview Scheduled → Round 2 → Round 3+ → Offer / Rejected / Withdrawn / **Link 404** |
| `Match Score` | number | 0–100 |
| `Job URL` | url | |
| `Approved?` | checkbox | **Only apply to rows where this is true** |
| `Resume` | file | |
| `Cover Letter` | file | |
| `Keywords` | text | JD keywords injected into tailored resume |
| `Date Found` | date | |
| `Date Applied` | date | |
| `Last Updated` | auto | |
| `Notes` | text | Match rationale, ATS info, comp range, flags |
| `Archetypes` | text | Format: `[PRIMARY-CODE] (primary) + [SECONDARY-CODE] (secondary). [Framing sentence].` |

### Page Body Structure

Every Notion tracker row is a full page. Inside the page body:

```
## Job Description
[Full, unabridged JD text — do not summarise or truncate]

---

## Tailored Resume
[Formatted resume text]

---

## Cover Letter
[Cover letter text]

---

## Analysis
Match Score: X/100
Archetype: [PRIMARY] (primary) + [SECONDARY] (secondary)
Framing: [one sentence]

Comp Research:
  Market range: [range]
  Negotiation anchor: [P60-75 value]
  Walk-away floor: [P40 value]

Rationale: [2-3 sentences]
Red Flags: [any flags]
Keywords Used: [comma list]
ATS: [platform] — posted [N] days ago
Legitimacy: [Proceed/Caution]
Date Found: [date]

---

## Interview Prep
[Links to interview prep sub-pages, added by Interview Prepper agent]
```

---

## Key Workflow Rules

- **Only apply to rows where `Approved? = true`** — never apply without user review
- If a job link returns 404 or is dead → mark Status = "Link 404" immediately, do not generate resume
- Resume and Cover Letter live as formatted text inside the page body (not just file attachments)
- A temporary PDF is generated on-demand for ATS upload, then deleted after submission
- Everything lives in Notion. No Google Drive.

---

## Storage Convention

| Item | Where it lives |
|------|---------------|
| Resume (formatted text) | Inside Notion page body, under `## Tailored Resume` |
| Cover letter (formatted text) | Inside Notion page body, under `## Cover Letter` |
| Full JD text | Inside Notion page body, under `## Job Description` |
| Temp resume PDF | `resumes/[Your-Name]-[Company]-[RoleSlug].pdf` — deleted after submission |
| Cover letter PDF | `resumes/[Your-Name]-[Company]-[RoleSlug]-Cover-Letter.pdf` — deleted after submission |
| Generation script | `resumes/gen_[company]_[role]_resume.py` — optionally kept for re-use |

---

## Application Process

**Applications are always submitted manually.** The pipeline stops after Notion Logger completes. The user:
1. Reviews the resume and cover letter in the Notion page body
2. Opens the job URL
3. Copies and pastes resume + cover letter into the ATS form
4. Submits
5. Updates Status = "Applied" and Date Applied in Notion

Do NOT attempt to automate form submission.

---

## Gmail Sync — Status Mapping

Monitor the Gmail address in `gmail.address` from `claude-job-profile.json` for emails from applied companies. Map signals to Notion status:

| Email signal | New Status |
|---|---|
| "application received", "thank you for applying" | Confirmation Received |
| "interview", "schedule a call", "next step", "video call" | Interview Scheduled |
| "second round", "next round", "technical interview" | Round 2 |
| "third round", "final round", "last stage" | Round 3+ |
| "offer", "pleased to offer", "compensation package" | Offer |
| "not moving forward", "other candidates", "unfortunately", "regret to inform" | Rejected |
| "withdrawn", "position has been filled" | Withdrawn |

If unclear → log to `working/gmail_ambiguous_{{DATE}}.json`. Do not guess.
