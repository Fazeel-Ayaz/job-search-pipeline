# Agent: Interview Prepper

## Context
Read before starting:
- `CLAUDE.md` — core rules, Notion IDs
- `context/profile.md` — work experience, metrics (for STAR answers), skills, side projects
- `context/infrastructure.md` — Notion schema (for creating the interview prep sub-page and linking it to the tracker row)
- `context/personal-questions.md` — general/personal question library (strengths, motivation, logistics), for screening or any round that includes personal-assessment questions

Do NOT load: `context/preferences.md`, `context/resume-format.md`

---

## Purpose
Run a structured interview prep session for a scheduled interview. Pulls the JD and tailored resume from Notion, identifies likely questions, and prepares structured answers using the candidate's real experience.

## Inputs
| Variable | Source |
|----------|--------|
| `{{NOTION_PAGE_URL}}` | URL of the Notion page for this role |
| `{{INTERVIEW_TYPE}}` | screening|behavioural|technical|case|final — ask user if unknown |
| `{{INTERVIEWER_ROLE}}` | Recruiter, Hiring Manager, Senior IC, Panel — ask user if unknown |
| `{{DATE}}` | Interview date if known |

## Story Library (always load first)

**Before generating any answers**, read `skills/star-library.md`. This file contains pre-written STAR stories, analytical frameworks, intro variants, and strengths/weaknesses. Use these as the primary source — prefer an existing story over generating a new one.

**Story re-use rule:** If an existing story fits the question at 70%+ relevance, use it with light adaptation for the company context. Only generate a new answer when no story maps to the question.

## Steps

### Step 1 — Pull context from Notion
Fetch the Notion page at `{{NOTION_PAGE_URL}}`. Extract:
- Company, role title, location
- Full JD text (from page body)
- Tailored resume text (## Tailored Resume section)
- Notes (## Notes section — includes match rationale and keywords)

### Step 2 — Load story library
Read `skills/star-library.md` and index the available stories by theme so they can be slotted to questions in Step 3.

### Step 3 — Identify likely questions by interview type

**Screening (recruiter):**
- "Walk me through your background" → check sheet for the best intro variant for this role type
- "Why this role / why {{COMPANY}}?" → use sheet answer if available; otherwise draft from research
- "What does your current role involve?"
- "What are your salary expectations?" → the candidate: "Open to market rate, happy to discuss"
- "Are you open to relocation?" → the candidate: yes, currently in [FROM_PROFILE: personal.location], targeting [FROM_PROFILE: personal.relocation_targets]

**Behavioural (hiring manager):**
Map to STAR format. Generate 5-7 questions based on the JD's core competencies. For each question, first check `skills/star-library.md` — use the question → story map there to find a pre-written answer before generating a new one. Common question themes:
- Cross-functional / alignment without authority → check star-library.md
- Retention / churn → check star-library.md
- Experimentation / A/B testing → check star-library.md
- Strategy or programme ownership → check star-library.md
- Product launch / GTM → check star-library.md
- Conflict / influencing up → check star-library.md
- Mistake / recovery → check star-library.md

**Technical / analytical:**
- "How would you design an A/B test for [specific product touchpoint in this JD]?"
- "How do you measure incrementality vs attribution?"
- "Walk me through your most complex analytical or modelling project" (pull the best fit from star-library.md)
- "What's your approach to cohort analysis?"
- If the Notion page or star-library.md has a pre-built analytical framework for this company, include it here

**Case study:**
- "{{SPECIFIC_METRIC}} at {{COMPANY}} has dropped X%. What do you do?"
- Invoke `agents/issue-tree-creator.md` for every case question: answer as a continuous spoken narrative across its four sequential steps (clarify the metric definition → structure broad, out loud → prioritize one branch with a benchmark/signal/cost-asymmetry hypothesis and a cheap confirm-or-kill check → land on a recommendation tied to a number, a timeframe, and a causality-isolation method) — never collapse the steps into one response, and never fall back to a loose "diagnose → hypothesise → experiment → measure" shorthand. A MECE tree is optional supporting visual for Step 2 only, used when the case is quantitative enough to warrant one — it is never the answer by itself
- If company tab has an existing case framework (e.g. a growth tree already built for this company), use it as the tree's starting structure rather than rebuilding from zero

### Step 4 — Write STAR answers
For each behavioural question:
1. First check the story library for a matching pre-written answer
2. If found: write out the full story in the prep sheet as C/T/A/R/L pointers (not a reference back to `star-library.md`), adapted for {{COMPANY}} context, followed by a **Landing guidance** sub-list — concrete delivery notes (what to lead with, how to translate metrics/language for {{COMPANY}}, pacing, what to emphasize if asked to go deeper)
3. If not found: draft from scratch using C/T/A/R/L format with real metrics only, plus the same Landing guidance sub-list

Keep answers 90–120 seconds when spoken aloud.

### Step 5 — Why this company
Research {{COMPANY}}'s current product focus, recent news, and growth challenges. Specifically cover:
1. **Core business model** — what the company does and the main products/services it offers
2. **Main competitors** — who they compete with and how {{COMPANY}} is positioned
3. **Business model insight relevant to the role** — how the specific function/segment {{TITLE}} sits in actually works (e.g. how the Acquire/Growth/CRM team drives revenue, what its core levers are)
4. **Most recent developments** — recent news, leadership changes, product launches, financial results

Use these four areas as the research base, then draft 3-4 sentences for the "Why {{COMPANY}}" answer showing genuine product understanding. Include a **Company Research** section in the prep sheet with the findings from all four areas (even details that don't make it into the spoken answer — useful for follow-up questions). Use the intro story variants in `skills/star-library.md` to inform which angle of the background to lead with.

### Step 6 — Questions to ask the interviewer
Generate 4-5 smart questions tailored to the role and company:
- About the team's tooling / experimentation maturity
- About the team's current focus (read from the JD's emphasis — e.g. growth vs retention vs efficiency)
- About success metrics for the role in the first 6 months
- One question showing the candidate has thought about a specific product or business challenge visible in the JD or recent company news

### Step 7 — Save to file
Save prep sheet to `working/interview_prep_{{COMPANY}}_{{DATE}}.md`.

### Step 8 — Create Notion interview prep page
Create a new Notion page as a child of the **existing job tracker page** for this role (not a new database row — a sub-page nested inside the existing row's page).

Use `mcp__eaaf596d-8c3c-4695-93b6-6fb9915a0cdf__notion-create-pages` with:
- `parent`: the page ID extracted from `{{NOTION_PAGE_URL}}` (the job tracker row page)
- `title`: `Interview Prep — {{INTERVIEW_TYPE}} — {{DATE}}`

Populate the page body with the full prep content using `mcp__eaaf596d-8c3c-4695-93b6-6fb9915a0cdf__notion-update-page`:

```
# Interview Prep — {{TITLE}} @ {{COMPANY}}
Type: {{INTERVIEW_TYPE}} | Interviewer: {{INTERVIEWER_ROLE}} | Date: {{DATE}}

---

## Quick Context
[3 bullets on what matters most for this role]

## Intro Story
[Which variant to use and the key points to hit]

## Likely Questions + Suggested Answers
[Full STAR answers — each labelled (library), (adapted), or (generated). For library/adapted stories, write out the full C/T/A/R/L story as pointers plus a Landing guidance sub-list — never just a reference back to star-library.md]

## Case Framework
[For technical/case rounds only]

## Why {{COMPANY}}
[Researched answer]

## Questions to Ask
[4-5 tailored questions]

## Watch-outs
[Red flags or tricky topics from the JD and Notion notes]
```

Then update the **parent job tracker page** using `mcp__eaaf596d-8c3c-4695-93b6-6fb9915a0cdf__notion-update-page` to append a link to the new prep page at the bottom of the page body:

```
---
## Interview Prep
[Interview Prep — {{INTERVIEW_TYPE}} — {{DATE}}]({{INTERVIEW_PREP_PAGE_URL}})
```

If the status on the tracker row is still "To Apply" or "Applied", update it to "Interview Scheduled" using `mcp__eaaf596d-8c3c-4695-93b6-6fb9915a0cdf__notion-update-page`.

### Step 9 — Confirm
Print:
```
✓ Interview prep saved to working/interview_prep_{{COMPANY}}_{{DATE}}.md
✓ Notion page created: {{INTERVIEW_PREP_PAGE_URL}}
✓ Linked from: {{NOTION_PAGE_URL}}
✓ Tracker status updated to: Interview Scheduled
```

If any Notion call fails, alert the user and fall back to the local .md file only.

## Format (page structure)
```
# Interview Prep — {{TITLE}} @ {{COMPANY}}
Type: {{INTERVIEW_TYPE}} | Interviewer: {{INTERVIEWER_ROLE}} | Date: {{DATE}}

---

## Quick Context
[3 bullets on what matters most for this role]

## Intro Story
[Which variant to use and why]

## Likely Questions + Suggested Answers
[For each question: label (library) / (adapted) / (generated)]
[Full STAR answer]

## Case Framework
[Only for technical/case rounds]

## Why {{COMPANY}}
[Researched 3-4 sentence answer]

## Questions to Ask
[4-5 tailored questions]

## Watch-outs
[Red flags or tricky topics]
```
