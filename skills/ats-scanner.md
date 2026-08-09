# Skill: ATS API Scanning

**Trigger:** Run when a new job URL is brought in, before scoring. The goal is to verify the role is still live and extract structured data directly from the ATS — not the job board. Job boards cache stale postings; ATS APIs reflect the actual open/closed state.

If the role is confirmed closed: skip scoring entirely, log as "Link 404" in Notion, and notify the user. Do not spend time on dead roles.

---

## Step 1: Detect the ATS

Inspect the job URL to identify which ATS is hosting the role.

| URL pattern | ATS | API available? |
|-------------|-----|---------------|
| `greenhouse.io`, `boards.greenhouse.io` | Greenhouse | ✅ Yes |
| `jobs.lever.co` | Lever | ✅ Yes |
| `jobs.ashbyhq.com` | Ashby | ✅ Yes |
| `smartrecruiters.com` | SmartRecruiters | ✅ Yes |
| `workday.com`, `myworkdayjobs.com` | Workday | ⚠️ No public API — use URL check |
| `linkedin.com/jobs` | LinkedIn (varies) | ⚠️ No — use link-verification fallback |
| `icims.com` | iCIMS | ❌ No public API |
| `taleo.net` | Taleo | ❌ No public API |
| `jobs.eu.lever.co` | Lever EU | ✅ Same as Lever |
| `apply.workable.com` | Workable | ✅ Yes |
| Custom company career site | Unknown | ⚠️ — try HEAD request |

If ATS cannot be determined: fall through to the link-verification skill.

---

## Step 2: Hit the ATS API

### Greenhouse

Extract the **company slug** and **job ID** from the URL:
- URL format: `https://boards.greenhouse.io/{slug}/jobs/{job_id}`
- Example: `https://boards.greenhouse.io/deliveryhero/jobs/5938271`

**API calls (use web_fetch):**

Check if job is still open:
```
GET https://boards-api.greenhouse.io/v1/boards/{slug}/jobs/{job_id}
```

List all open jobs (confirm the job is in the list):
```
GET https://boards-api.greenhouse.io/v1/boards/{slug}/jobs
```

**Response to check:**
- `"status": "open"` → role is live
- If 404 or job not in list → role is closed

**Data to extract from response:**
- `title` — exact job title
- `updated_at` — last updated date (stale if >60 days ago with no update)
- `location.name` — confirmed location
- `departments[0].name` — team/department

---

### Lever

Extract the **company slug** and **posting ID**:
- URL format: `https://jobs.lever.co/{slug}/{posting_id}`
- Example: `https://jobs.lever.co/spotify/abc123-def456`

**API call:**
```
GET https://api.lever.co/v0/postings/{slug}/{posting_id}?mode=json
```

List all open postings:
```
GET https://api.lever.co/v0/postings/{slug}?mode=json
```

**Response to check:**
- If 200 with posting data → role is live
- If 404 → role is closed

**Data to extract:**
- `text` — job title
- `createdAt` (Unix timestamp) — posted date
- `categories.location` — confirmed location
- `categories.team` — team/department

---

### Ashby

Extract the **company slug** from the URL:
- URL format: `https://jobs.ashbyhq.com/{slug}/{job_id}`

**API call:**
```
POST https://jobs.ashbyhq.com/api/non-user-facing/posting-board/listings
Body: { "organizationHostedJobsPageName": "{slug}" }
```

Or for a single job:
```
GET https://jobs.ashbyhq.com/api/non-user-facing/posting/{job_id}
```

**Response to check:** If job appears in listings → live. If 404 → closed.

---

### SmartRecruiters

- URL format: `https://jobs.smartrecruiters.com/{CompanyName}/{job_id}`

**API call:**
```
GET https://api.smartrecruiters.com/v1/companies/{CompanyName}/postings/{job_id}
```

**Response:** `"status": "PUBLISHED"` → live; anything else or 404 → closed.

---

### Workable

- URL format: `https://apply.workable.com/{slug}/j/{job_id}`

**API call:**
```
GET https://apply.workable.com/api/v3/accounts/{slug}/jobs/{job_id}
```

---

### Workday (no API — URL check)

Workday does not expose a public API. Use `web_fetch` on the job URL directly:
- If page loads with job content → likely still live
- If 404 or redirects to `/jobs` homepage → closed
- Check for "This job is no longer available" text in the page body

---

## Step 3: Extract Posted Date + Staleness Check

Once the API call confirms the role is live, check how old the posting is:

| Posted age | Interpretation | Action |
|------------|---------------|--------|
| < 14 days | Fresh — high priority | Proceed immediately |
| 14–30 days | Normal | Proceed |
| 31–60 days | Aging — may still be active | Note in Notion, proceed with caution |
| 60–90 days | Likely stale or ghosting | Flag to user — ask if they want to proceed |
| 90+ days | Almost certainly ghost posting | Flag strongly — recommend skipping unless company confirmed it's active |

If posted date is unavailable: check the LinkedIn posting date as a proxy (note: LinkedIn adds 30 days by default).

---

## Step 4: Output

Always state the ATS scan result before the score rubric runs:

```
ATS Scan:
  ATS:          Greenhouse (boards.greenhouse.io/deliveryhero)
  Status:       ✅ Open
  Posted:       2026-05-14 (24 days ago)
  Last updated: 2026-05-28
  Department:   Marketing / Lifecycle
  Location:     Amsterdam, Netherlands (confirmed)
  Staleness:    Normal — proceed
```

Or if closed:
```
ATS Scan:
  ATS:     Lever (jobs.lever.co/spotify)
  Status:  ❌ CLOSED — 404 from API
  Action:  Do not apply. Logging as "Link 404" in Notion.
```

---

## Step 5: Log to Notion

- If role is **live**: add `ATS: [ATS name], confirmed open [date], posted [X] days ago` to the Notes field
- If role is **closed**: set Status to "Link 404" and add `ATS scan: confirmed closed [date]` to Notes
- If ATS **unknown**: add `ATS: unknown — manual verification needed` and proceed with link-verification fallback

---

## Fallback: No API Available

If the ATS has no public API (Taleo, iCIMS, custom site):
1. `web_fetch` the job URL directly
2. Check HTTP status code — 404 = closed
3. Look for "no longer available", "position filled", "this job has closed" in page text
4. If none found: treat as live, note "manual check" in Notion
5. Run `link-verification` skill as the final fallback
