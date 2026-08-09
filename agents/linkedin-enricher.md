# Agent: LinkedIn Enricher

## Context
Read before starting:
- `CLAUDE.md` — core rules
- `context/preferences.md` — target companies and archetypes (for indexing connections by relevance)
- `context/profile.md` — current work experience (for cross-referencing connections against your career history)

Do NOT load: `context/resume-format.md`, `context/infrastructure.md`

---

## Purpose
Two jobs: (1) enrich CLAUDE.md and the job profile with accurate data from the LinkedIn archive; (2) index connections for the LinkedIn Connections referral skill. Run once when a new archive is downloaded, then as needed when the archive is refreshed.

## Trigger
Run when the user says the LinkedIn archive has been downloaded and extracted to:
`{{JOB_SEARCH_DIR}}/linkedin-archive/`

## Inputs
| Variable | Source |
|----------|--------|
| `{{ARCHIVE_PATH}}` | `{{JOB_SEARCH_DIR}}/linkedin-archive/` |
| `{{DATE}}` | Current date |

---

## Step 1 — Verify Archive Contents

Check which files are present in `{{ARCHIVE_PATH}}`:
```bash
ls {{JOB_SEARCH_DIR}}/linkedin-archive/
```

Expected files (LinkedIn exports these by default):
- `Connections.csv` — all 1st-degree connections
- `messages.csv` — DM history
- `Profile.csv` — profile summary
- `Positions.csv` (sometimes) — work history with exact dates
- `Skills.csv` (sometimes) — skills and endorsements
- `Education.csv` (sometimes) — education history

Note which are missing and proceed with what's available.

---

## Step 2 — Build Connections Index

Read `Connections.csv`. Expected columns: `First Name`, `Last Name`, `Email Address`, `Company`, `Position`, `Connected On`.

Build and save a Python dict to `working/linkedin_connections_index_{{DATE}}.json`:

```python
import csv, json

connections = []
with open("linkedin-archive/Connections.csv", encoding='utf-8-sig') as f:
    reader = csv.DictReader(f)
    for row in reader:
        connections.append({
            "name": f"{row.get('First Name','')} {row.get('Last Name','')}".strip(),
            "company": row.get('Company', '').strip(),
            "company_normalized": row.get('Company', '').lower().strip()
                .replace(' inc.','').replace(' ltd','').replace(' gmbh','')
                .replace(' b.v.','').replace(' s.a.','').replace(' plc',''),
            "position": row.get('Position', '').strip(),
            "email": row.get('Email Address', '').strip(),
            "connected_on": row.get('Connected On', '').strip()
        })

# Save
with open("working/linkedin_connections_index_{{DATE}}.json", "w") as f:
    json.dump(connections, f, indent=2)

print(f"Indexed {len(connections)} connections")
```

Run this script via Bash. Report the total connection count to the user.

---

## Step 3 — Enrich Job Profile from Archive

### 3a. Read Profile.csv (if present)
Extract and compare against CLAUDE.md:
- Current role title (verify matches CLAUDE.md)
- Connections count (note in output — useful context)
- Location (should match [FROM_PROFILE: personal.location])
- Profile URL (should be {{YOUR_LINKEDIN_URL}})

### 3b. Read Positions.csv (if present)
Cross-check role dates and titles against CLAUDE.md. Flag any discrepancies:

| Archive says | CLAUDE.md says | Action |
|-------------|---------------|--------|
| Different start date | Different date | Flag — update CLAUDE.md if archive is more accurate |
| Different title | Different title | Flag for user to decide canonical version |
| Role not in CLAUDE.md | Missing | Add to CLAUDE.md if substantive |

### 3c. Read messages.csv (if present)
Scan for:
- Messages from recruiters about job opportunities (flag to user — may be active leads)
- Message history with people at target companies (enriches warmth data in connections index)
- Any pending follow-ups (flagged opportunities that may need a reply)

**Privacy note:** Do not log personal message content. Only extract: sender company, date, subject/topic signal, whether it was a job-related outreach.

Recruiter message pattern (flag these):
- Subject mentions: "opportunity", "role", "position", "hiring", "reach out", a job title
- Sender position contains: "recruiter", "talent", "HR", "people", "headhunter"

Output flagged recruiter messages as:
```
Recruiter outreach found in messages.csv:
  - [Name] ([Company]) — [Date] — [Topic signal]
  Action: review and respond if relevant
```

---

## Step 4 — Generate Connections Summary

Produce a summary for the user:

```
=== LinkedIn Archive Enrichment Complete ===
Date: {{DATE}}
Archive path: {{ARCHIVE_PATH}}

Connections:
  Total indexed: [N]
  By top companies (target list):
    Uber:           [N]
    Delivery Hero:  [N]
    Spotify:        [N]
    Revolut:        [N]
    Bolt:           [N]
    Wise:           [N]
    HelloFresh:     [N]
    Wolt:           [N]
    [show all target companies with N > 0]

  Notable connections (same function — Growth/CRM/Lifecycle/Marketing):
    - [Name], [Title] @ [Company]
    - [Name], [Title] @ [Company]
    [top 10 most relevant]

Recruiter messages detected: [N]
  [List if any — see above]

Profile discrepancies vs CLAUDE.md:
  [List any mismatches found in Step 3b]
  [Or: "No discrepancies found"]
```

---

## Step 5 — Update Working Files

Save the connections index to:
`working/linkedin_connections_index_{{DATE}}.json`

This is the file that `skills/linkedin-connections.md` reads when matching connections against job postings. The pipeline will auto-use the most recent index file.

If an older index exists, archive it:
`working/linkedin_connections_index_{{PREV_DATE}}.json.archived`

---

## Rules

- Never read message content beyond what's needed to detect recruiter outreach
- Never log personal conversation content to Notion or working files
- Never act on recruiter messages without explicitly flagging to user first
- The connections index is a local working file — never upload to any external service
- If Connections.csv is missing or empty, alert user and stop

## Output

```json
{
  "connections_count": 847,
  "index_path": "working/linkedin_connections_index_{{DATE}}.json",
  "recruiter_messages": 3,
  "profile_discrepancies": [],
  "top_target_company_connections": {
    "Uber": 4,
    "Delivery Hero": 12,
    "Spotify": 2
  }
}
```
