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
Apply **Score Rubric skill** (`skills/score-rubric.md`) to each candidate. Score across all 6 dimensions:

| Dimension | Max | Scoring notes |
|-----------|-----|--------------|
| Industry / vertical match | 20 | Consumer tech, marketplace, food delivery, fintech = 20; adjacent (e-commerce, healthtech) = 12; unrelated = 0 |
| JD lifecycle/CRM signal density | 20 | 5+ signals from include list = 20; 3-4 = 14; 1-2 = 7; 0 = 0 |
| Required experience met | 15 | Years required ≤ the candidate's years in comparable role = 15; 1yr gap = 10; 2yr gap = 5 |
| JD keywords present in profile | 15 | >80% keyword overlap = 15; 60–80% = 10; 40–60% = 6; <40% = 0 |
| Seniority signals match | 15 | "Senior Specialist", "Manager", "Lead" = 15; "Specialist" = 12; "Associate" = 5; "Director"/"Head" = 8 |
| Location / visa sponsorship | 15 | UAE = 15; EU with visa sponsorship confirmed or likely = 15; EU with no mention = 10; no relocation = 0 |

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
