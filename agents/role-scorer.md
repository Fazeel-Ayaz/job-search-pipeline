# Agent: Role Scorer

## Context
Read before starting:
- `CLAUDE.md` — core rules, scoring thresholds (60+ to qualify, top 15)
- `context/preferences.md` — JD signals, role archetypes, geography scoring notes, target companies

Do NOT load: `context/profile.md`, `context/resume-format.md`, `context/infrastructure.md`

---

## Purpose
Score each candidate role against the candidate's 100-point match rubric. Keep roles scoring 60+. Produce a ranked shortlist.

## Inputs
| Variable | Source |
|----------|--------|
| `{{CANDIDATES_FILE}}` | Path to `working/candidates_{{DATE}}.json` |
| `{{DATE}}` | Current date YYYY-MM-DD |

## Steps

### Step 0 — Pre-condition check
Before scoring any candidate, confirm both of these have run:
- **ATS scan** (`skills/ats-scanner.md`): posting must be confirmed open (or ATS unknown). If `ats_status: closed` → remove from candidates, mark Link 404.
- **Legitimacy check** (`skills/legitimacy-check.md`): verdict must be Proceed or Caution. If `legitimacy_verdict: Skip` → remove from candidates.

If the candidates file was produced by Job Discovery and these checks have not yet run, run them now before proceeding to scoring.

### Step 1 — Load candidates
Read `{{CANDIDATES_FILE}}`. For each candidate, load the full JD (from `full_jd` field or fetch via JD Reader agent if missing).

### Step 2 — Apply Score Rubric skill
Apply **Score Rubric skill** (`skills/score-rubric.md`) to each candidate. That file contains the full scoring criteria for all 6 dimensions — read it before scoring any candidate. Do not use cached dimension criteria from memory.

### Step 3 — Log scores
For each candidate, record:
```json
{
  "title": "...",
  "company": "...",
  "location": "...",
  "url": "...",
  "score": 74,
  "score_breakdown": {
    "industry": 16,
    "jd_signals": 20,
    "experience": 15,
    "keywords": 10,
    "seniority": 8,
    "location": 5
  },
  "top_matching_signals": ["retention", "braze", "A/B testing", "lifecycle"],
  "missing_keywords": ["LTV modelling", "CleverTap"],
  "red_flags": ["Requires fluent German"],
  "qualify": true,
  "ats": "Greenhouse",
  "ats_status": "open",
  "posting_age_days": 18,
  "legitimacy_verdict": "Proceed",
  "legitimacy_notes": "5 green / 0 red"
}
```

### Step 4 — Filter and rank
Keep only roles with `score >= 60`. Sort descending by score. Cap at 15 roles.

### Step 5 — Output
Save ranked shortlist to `working/shortlist_{{DATE}}.json`. Print a summary table to console:
```
Rank | Score | Company          | Title                              | Location
1    | 87    | Wolt             | Global Lifecycle Mktg Mgr          | Helsinki
2    | 82    | Delivery Hero    | Growth Marketing Manager           | Berlin
...
```

## Output
`working/shortlist_{{DATE}}.json` — ranked, scored shortlist ready for resume tailoring
