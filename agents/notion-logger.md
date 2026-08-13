# Agent: Notion Logger

## Context
Read before starting:
- `CLAUDE.md` — core rules, Notion IDs (Database ID, Parent Page ID, Data Source ID)
- `context/infrastructure.md` — full Notion schema, page body structure, storage convention, key workflow rules

Do NOT load: `context/profile.md`, `context/preferences.md`, `context/resume-format.md`

---

## Purpose
Create a new row in the Job Application Tracker database and populate the corresponding Notion page with the tailored resume, cover letter, and notes.

## Inputs
| Variable | Source |
|----------|--------|
| `{{TITLE}}` | Role title |
| `{{COMPANY}}` | Company name |
| `{{LOCATION}}` | Role location |
| `{{JOB_URL}}` | Job posting URL |
| `{{JOB_DESCRIPTION}}` | Full, unabridged job description text as posted (do not summarize or truncate) |
| `{{SCORE}}` | Match score /100 |
| `{{KEYWORDS_USED}}` | Comma-separated keywords injected into resume |
| `{{RESUME_TEXT}}` | Formatted resume text (from Resume Tailor agent) |
| `{{COVER_LETTER_TEXT}}` | Cover letter text (from Cover Letter Writer agent) |
| `{{MATCH_RATIONALE}}` | 2-3 sentence explanation of why this role qualifies |
| `{{RED_FLAGS}}` | Any flags noted (language requirement, visa risk, etc.) |
| `{{DATE}}` | Current date YYYY-MM-DD |
| `{{ARCHETYPE_PRIMARY}}` | Primary archetype code from Resume Tailor (as defined in skills/archetypes.md) |
| `{{ARCHETYPE_SECONDARY}}` | Secondary archetype code (as defined in skills/archetypes.md) |
| `{{ARCHETYPE_FRAMING}}` | One-sentence framing summary from archetype detection |
| `{{COMP_RANGE}}` | Market salary range from Comp Research skill |
| `{{COMP_ANCHOR}}` | Negotiation anchor (P60-75) |
| `{{LEGITIMACY_VERDICT}}` | Proceed / Caution from Legitimacy Check skill |
| `{{ATS_NAME}}` | ATS platform (Greenhouse, Lever, etc.) |
| `{{POSTING_AGE}}` | Days since posting (from ATS scan) |

## Notion Config
- **Database ID:** {{NOTION_DATABASE_ID}}
- **Parent Page:** {{NOTION_PARENT_PAGE_ID}}
- **Data Source ID:** collection://{{NOTION_DATA_SOURCE_ID}}

## Steps

### Step 0 — Resolve Data Source ID

Before creating any rows, confirm the Data Source ID is real (not a placeholder).

Read `notion.data_source_id` from `claude-job-profile.json`. If it is missing, empty, or still reads `YOUR_NOTION_DATA_SOURCE_ID`:

1. Call `notion-fetch` with the database_id (from `notion.database_id` in the profile).
2. In the response, find the `<data-source url="collection://...">` tag. The full `collection://...` string is the Data Source ID.
3. Write it back to `claude-job-profile.json` under `notion.data_source_id`.
4. Use this value as `{{NOTION_DATA_SOURCE_ID}}` for all calls in this session.

If the fetch fails or returns no data-source tag, alert the user: the Notion integration is not connected to the database. Refer them to setup Phase 4.3.

### Step 1 — Create database row

**Critical: the `parent` argument is required on the create-pages call itself.** If `parent` is omitted, Notion silently creates a private workspace-level page instead of a database row — the call still succeeds and returns a page ID, but Role Title and Approved? are the only properties that actually persist; Company, Location, Status, Match Score, Job URL, Keywords, Date Found, Archetypes, and Notes all come back empty even though you passed them. There is no error to catch this — it fails silently. Always call `mcp__eaaf596d-8c3c-4695-93b6-6fb9915a0cdf__notion-create-pages` with:
```
parent: { "type": "data_source_id", "data_source_id": "{{NOTION_DATA_SOURCE_ID}}" }
```

Set properties in the same call:
```
Role Title (title):     {{TITLE}}
Approved? (checkbox):   "__NO__"
```

Then immediately follow with a second call, `mcp__eaaf596d-8c3c-4695-93b6-6fb9915a0cdf__notion-update-page` with `command: "update_properties"`, to set everything else (text/select/number/url/date properties don't reliably persist when set in the same create-pages call as a non-title property):
```
Company (text):         {{COMPANY}}
Location (text):        {{LOCATION}}
Status (select):        To Apply
Match Score (number):   {{SCORE}}
Job URL (url):          {{JOB_URL}}
Keywords (text):        {{KEYWORDS_USED}}
date:Date Found:start:  {{DATE}}
date:Date Found:is_datetime: 0
Archetypes (text):      {{ARCHETYPE_PRIMARY}} (primary) + {{ARCHETYPE_SECONDARY}} (secondary). {{ARCHETYPE_FRAMING}}
Notes (text):           Match score: {{SCORE}}/100. {{MATCH_RATIONALE}} | ATS: {{ATS_NAME}}, posted {{POSTING_AGE}} days ago. Legitimacy: {{LEGITIMACY_VERDICT}}. Comp: {{COMP_RANGE}} — anchor {{COMP_ANCHOR}}. Red flags: {{RED_FLAGS}}
```

**Always verify after logging:** call `notion-fetch` on the new page ID and confirm every property above actually shows a value (not empty string). Do not trust the create/update call's success response alone — it returns 200 even when properties silently failed to persist.

### Step 2 — Populate page body
Use `mcp__eaaf596d-8c3c-4695-93b6-6fb9915a0cdf__notion-update-page` to add content blocks to the new page:

```
## Job Description

{{JOB_DESCRIPTION}}

---

## Tailored Resume

{{RESUME_TEXT}}

---

## Cover Letter

{{COVER_LETTER_TEXT}}

---

## Analysis

Match Score: {{SCORE}}/100
Archetype: {{ARCHETYPE_PRIMARY}} (primary) + {{ARCHETYPE_SECONDARY}} (secondary)
Framing: {{ARCHETYPE_FRAMING}}

Comp Research:
  Market range: {{COMP_RANGE}}
  Negotiation anchor: {{COMP_ANCHOR}}
  Walk-away floor: {{COMP_FLOOR}}

Rationale: {{MATCH_RATIONALE}}
Red Flags: {{RED_FLAGS}}
Keywords Used: {{KEYWORDS_USED}}
ATS: {{ATS_NAME}} — posted {{POSTING_AGE}} days ago
Legitimacy: {{LEGITIMACY_VERDICT}}
Date Found: {{DATE}}
```

### Step 3 — Confirm and return
Return:
```json
{
  "notion_page_id": "...",
  "notion_page_url": "https://notion.so/...",
  "status": "To Apply",
  "approved": false
}
```

Print confirmation: `✓ Logged: {{TITLE}} @ {{COMPANY}} — Score: {{SCORE}} — Awaiting approval`

## Rules
- Always set `Approved? = false` on creation — user reviews before applying
- Never set Status to "Applied" in this agent — the user updates this manually after submitting the application
- If the Notion API call fails, save the full structured data to `working/notion_failed_{{DATE}}.json` and alert the user
