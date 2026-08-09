# Agent: JD Reader

## Context
Read before starting:
- `CLAUDE.md` — core rules (Link Verification skill, dead link handling)

Do NOT load: `context/profile.md`, `context/preferences.md`, `context/resume-format.md`, `context/infrastructure.md`
This is a fetch-only agent. It does not score, write, or log.

---

## Purpose
Fetch and parse a full job description from a URL. Handles company career pages, ATS systems (Greenhouse, Lever, Ashby, Workday), and aggregators. Returns structured JD data.

## Inputs
| Variable | Source |
|----------|--------|
| `{{JOB_URL}}` | URL of the job posting |
| `{{COMPANY}}` | Company name (for context) |
| `{{TITLE}}` | Role title (for context) |

## Steps

### Step 1 — Attempt direct fetch
Use `mcp__workspace__web_fetch` on `{{JOB_URL}}`. If content is returned and contains role description text → proceed to Step 3.

### Step 2 — Fallback to Claude in Chrome
If web_fetch returns a shell, spinner, or "enable JavaScript" → the page is client-rendered. Use `mcp__Claude_in_Chrome__navigate` to `{{JOB_URL}}`, then `mcp__Claude_in_Chrome__get_page_text` to extract rendered content.

If the URL returns 404 or the page doesn't load → STOP. Return `{"status": "dead", "url": "{{JOB_URL}}"}`. The caller must mark this role as **Link 404** in Notion immediately.

### Step 3 — Extract structured JD
From the fetched text, extract:
```json
{
  "title": "exact title from page",
  "company": "{{COMPANY}}",
  "location": "city, country",
  "url": "{{JOB_URL}}",
  "jd_text": "full job description text",
  "requirements": ["requirement 1", "requirement 2"],
  "responsibilities": ["responsibility 1", "responsibility 2"],
  "tools_mentioned": ["Braze", "Amplitude", "SQL"],
  "keywords": ["retention", "lifecycle", "A/B testing", "cohort"],
  "years_required": 3,
  "seniority": "Senior|Mid|Lead|Manager",
  "visa_sponsorship_mentioned": true|false|null
}
```

### Step 4 — Apply Link Verification skill
Check the URL against the **Link Verification skill** (`skills/link-verification.md`). Flag aggregator URLs. Prefer direct ATS URLs over aggregator links.

### Step 5 — Run ATS Scanner
Apply the **ATS Scanner skill** (`skills/ats-scanner.md`):
- Detect the ATS from the URL pattern (Greenhouse, Lever, Ashby, Workday, Workable, SmartRecruiters, etc.)
- Hit the ATS API directly to confirm whether the posting is still open
- Extract the posted date and last updated date if available
- If ATS confirms **closed**: STOP. Return `{"status": "dead", "ats_closed": true, "url": "{{JOB_URL}}"}`. Caller must mark as **Link 404** in Notion.
- If ATS is unknown or has no public API: attempt a HEAD/GET on the URL; record `ats_status: "unknown — URL check only"`

### Step 6 — Run Legitimacy Check
Apply the **Legitimacy Check skill** (`skills/legitimacy-check.md`):
- Score green/red flags against the 14-signal checklist
- Produce the verdict: Proceed / Caution / Skip
- If **Skip**: STOP. Return `{"status": "skip", "legitimacy": "skip", "reason": "..."}`. Do not proceed to scoring.
- If **Caution**: continue but carry the caution note in the output

## Output
Structured JD object. Returned inline or saved to `working/jd_{{COMPANY}}_{{SLUG}}.json`.

```json
{
  "title": "exact title from page",
  "company": "{{COMPANY}}",
  "location": "city, country",
  "url": "{{JOB_URL}}",
  "jd_text": "full job description text",
  "requirements": ["requirement 1", "requirement 2"],
  "responsibilities": ["responsibility 1", "responsibility 2"],
  "tools_mentioned": ["Braze", "Amplitude", "SQL"],
  "keywords": ["retention", "lifecycle", "A/B testing", "cohort"],
  "years_required": 3,
  "seniority": "Senior|Mid|Lead|Manager",
  "visa_sponsorship_mentioned": true,
  "ats": "Greenhouse",
  "ats_status": "open",
  "posted_date": "2026-05-20",
  "posting_age_days": 18,
  "legitimacy_verdict": "Proceed",
  "legitimacy_notes": "5 green / 0 red — ATS-hosted, company verified, salary stated"
}
```
