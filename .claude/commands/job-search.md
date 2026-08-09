---
description: Scan all job sources, score results, and log qualifying roles to Notion. No resume generation.
allowed-tools: Read, Write, Bash, WebFetch, WebSearch, mcp__Claude_in_Chrome__navigate, mcp__Claude_in_Chrome__get_page_text, mcp__eaaf596d-8c3c-4695-93b6-6fb9915a0cdf__notion-create-pages, mcp__eaaf596d-8c3c-4695-93b6-6fb9915a0cdf__notion-update-page, mcp__eaaf596d-8c3c-4695-93b6-6fb9915a0cdf__notion-fetch
---

# /job-search

## Context
Load before starting:
- `CLAUDE.md`
- `context/preferences.md`

---

## Step 1 — Scan
Run the scanner and save output to a dated file. The scanner ALWAYS exits 0 — even if zero
candidates pass filters. Do not treat empty output as an error or failure.

```bash
python3 job_scanner.py --output "working/candidates_$(date +%Y-%m-%d).json"
```

Read the output file. If it contains `[]` (empty array):
- Print: "Scanner returned 0 candidates after pre-filtering. Check working/candidates_$(date +%Y-%m-%d).json for raw debug info."
- Stop. Do not proceed to Step 2.

If it contains candidates, continue.

## Step 2 — ATS Check (every candidate)
Run `skills/ats-scanner.md` on every URL in the candidate list.
- Dead / 404 / closed → drop immediately. No further processing for that role.
- Open or ATS unknown → keep.

## Step 3 — Legitimacy Check (ATS survivors only)
Run `skills/legitimacy-check.md` on the snippet for each surviving candidate.
- Skip verdict → drop. Do not fetch JD.
- Caution verdict → keep. Note the flag — it will go into Notion Notes.
- Proceed verdict → keep.

## Step 4 — Fetch Full JDs (legitimacy survivors only)
For each role still standing, use `agents/jd-reader.md` to fetch the full job description text.
Do not fetch JDs for roles that were dropped — wasted tokens.

## Step 5 — JD Filter (full text)
Run `skills/jd-filter.md` on each full JD.
Record for each role: signals found, red flags, confidence level (High / Medium / Low).

## Step 6 — Score
Run `skills/score-rubric.md` on each full JD.
Keep only roles scoring 60+. Cap at 15 roles, ranked descending by score.
Drop the rest — do not log them.

## Step 7 — Archetype + Comp (60+ roles only)
For each qualifying role:
1. Run `skills/archetypes.md` — detect primary and secondary archetype with signal counts.
2. Run `skills/comp-research.md` — build P25/P50/P75 market range, set negotiation anchor (P60–75) and walk-away floor (P40).

## Step 8 — Log to Notion
Run `agents/notion-logger.md` for each qualifying role.

**Properties:**
- Role Title, Company, Location
- Status = "To Apply"
- Approved? = false
- Match Score
- Job URL
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

No resume. No cover letter. These come after approval via /filling-in.

---

## Stop here
Print a summary table: rank, score, company, title, location.
Do not run any further steps. User reviews in Notion and sets Approved? = true for roles to pursue.
