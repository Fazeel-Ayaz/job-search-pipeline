---
description: Scope a single job URL — ATS check, fetch JD, legitimacy check, score, archetype, comp research, log to Notion. No resume generation.
allowed-tools: Read, Write, Bash, WebFetch, WebSearch, mcp__Claude_in_Chrome__navigate, mcp__Claude_in_Chrome__get_page_text, mcp__eaaf596d-8c3c-4695-93b6-6fb9915a0cdf__notion-create-pages, mcp__eaaf596d-8c3c-4695-93b6-6fb9915a0cdf__notion-update-page, mcp__eaaf596d-8c3c-4695-93b6-6fb9915a0cdf__notion-fetch
---

# /job-scope

URL: $ARGUMENTS

## Context
Load before starting:
- `CLAUDE.md`
- `context/preferences.md`

---

## Step 1 — ATS Check
Run `skills/ats-scanner.md` on $ARGUMENTS.
- Dead / 404 / closed → stop. Report: "Dead link — not logged." Do nothing further.
- Open or ATS unknown → continue.

## Step 2 — Fetch Full JD
Use `agents/jd-reader.md` to fetch the full job description from $ARGUMENTS.

## Step 3 — Legitimacy Check
Run `skills/legitimacy-check.md` on the full JD.
- Skip verdict → stop. Report reason. Do not log.
- Caution verdict → continue. Flag for Notion Notes.
- Proceed verdict → continue.

## Step 4 — JD Filter
Run `skills/jd-filter.md` on the full JD.
Record: signals found, red flags, confidence level (High / Medium / Low).

## Step 5 — Score
Run `skills/score-rubric.md`.
If score < 60 → stop. Report the score and the two weakest dimensions. Do not log.

## Step 6 — Archetype + Comp
1. Run `skills/archetypes.md` — detect primary and secondary archetype with signal counts.
2. Run `skills/comp-research.md` — build P25/P50/P75 market range, set negotiation anchor (P60–75) and walk-away floor (P40).

## Step 7 — Log to Notion
Run `agents/notion-logger.md`.

**Properties:**
- Role Title, Company, Location
- Status = "To Apply"
- Approved? = false
- Match Score
- Job URL = $ARGUMENTS
- Keywords (top matching JD keywords)
- Date Found = today
- Archetypes = "[PRIMARY] (primary) + [SECONDARY] (secondary). [Framing sentence]."
- Notes = ATS result · Legitimacy verdict · Comp range · Negotiation anchor · Match rationale · Any flags

**Page body (strict order):**
```
## Job Description
[Full unabridged JD text — never summarise or truncate]

## JD Filter
Signals found: [list]
Red flags: [list]
Confidence: High / Medium / Low

## Score Breakdown
Total: [X]/100
Industry match: [X]/20
JD signal density: [X]/20
Experience match: [X]/15
Keyword overlap: [X]/15
Seniority signals: [X]/15
Location/visa: [X]/15

## Archetype Detection
Primary: [CODE] — [N signals]: [list]
Secondary: [CODE] — [N signals]: [list]
Framing: [one sentence]

## Comp Research
Market range: [P25] – [P75]
Negotiation anchor: [P60–75 value]
Walk-away floor: [P40 value]
Sources: [brief note]
```

No resume. No cover letter.

---

## Stop here
Report: score, archetype, comp range, any flags.
User reviews in Notion and sets Approved? = true to proceed to /filling-in.
