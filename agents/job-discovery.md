# Agent: Job Discovery

## Context
Read before starting:
- `CLAUDE.md` — core rules, IDs, hard exclusions, skills table
- `context/preferences.md` — target archetypes, JD signals, geography, deal-breakers, recently applied list, target companies

Do NOT load: `context/profile.md`, `context/resume-format.md`, `context/infrastructure.md`

---

## Purpose
Scan all configured job sources for roles matching the candidate's profile. Pre-filter before Claude reads anything. Return a deduplicated candidate list ready for scoring.

## Inputs
| Variable | Source |
|----------|--------|
| `{{DATE}}` | Current date YYYY-MM-DD |
| `{{MAX_RESULTS}}` | Default 30 (pre-filter), keep top 15 after scoring |
| `{{COUNTRIES}}` | ae, de, nl, gb, se, fi, ee, be, fr — from CLAUDE.md geography |

## Steps

### Step 1 — Run job_scanner.py
```
python3 job_scanner.py --output working/candidates_{{DATE}}.json
```
This hits 11 sources: Adzuna (10 countries), Reed UK, aijobs.net, The Muse, Remotive, Jobicy, Arbeitnow, Greenhouse (per-company), Lever (per-company), JSearch (RapidAPI), and Indeed Scraper (RapidAPI). Pre-filtered JSON is written to `working/candidates_{{DATE}}.json` and also printed to stdout.

To skip RapidAPI sources (saves rate limit quota): add `--skip-rapidapi`
To change recency window: add `--max-age 7` (default: 14 days)

### Step 2 — Load and review results
Read `working/candidates_{{DATE}}.json`. For each result, check:
- Is the company in `excluded_companies_by_country` (Indian-headquartered)? → drop
- Does the title contain hard-exclude terms (sales, business development, account management, performance marketing, media buying)? → drop
- Is it already in `recently_applied` list in CLAUDE.md? → drop
- Is it already in `scanned_history.json`? → drop

### Step 3 — Apply JD Filter skill
For each surviving result, apply the **JD Filter skill** (`skills/jd-filter.md`). If the snippet alone is strong enough → tentative include. If ambiguous → flag for Step 4. If clear exclude signal → drop.

### Step 4 — Fetch full JDs for ambiguous results
For each flagged result, use Claude in Chrome to navigate to the job URL and extract the full JD text. Re-apply JD Filter skill with full text. Include or drop accordingly.

### Step 5 — Output candidate list
Return a JSON array saved to `working/candidates_{{DATE}}.json`:
```json
[
  {
    "title": "...",
    "company": "...",
    "location": "...",
    "url": "...",
    "source": "adzuna|reed|muse|remotive|jobicy|arbeitnow|greenhouse|lever",
    "snippet": "...",
    "full_jd": "...",
    "jd_signals": ["retention", "braze", "A/B testing"],
    "pre_filter_pass": true
  }
]
```

### Step 6 — Handoff
Pass `working/candidates_{{DATE}}.json` to the **Role Scorer agent**.

## Output
`working/candidates_{{DATE}}.json` — pre-filtered candidate list with JD text and signals
