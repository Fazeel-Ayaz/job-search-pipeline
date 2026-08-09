---
description: Generate structured interview prep for a scheduled interview. Pulls context from Notion, writes story-driven STAR answers, researches company, creates Notion sub-page.
allowed-tools: Read, Write, Bash, WebFetch, WebSearch, mcp__Claude_in_Chrome__navigate, mcp__Claude_in_Chrome__get_page_text, mcp__eaaf596d-8c3c-4695-93b6-6fb9915a0cdf__notion-create-pages, mcp__eaaf596d-8c3c-4695-93b6-6fb9915a0cdf__notion-update-page, mcp__eaaf596d-8c3c-4695-93b6-6fb9915a0cdf__notion-fetch
---

# /interview-prep

Notion page URL: $ARGUMENTS

## Context
Load before starting:
- `CLAUDE.md`
- `context/profile.md`
- `context/infrastructure.md`

---

## Step 1 — Ask the user (before doing anything else)
Ask:
1. Interview type: screening / behavioural / technical / case / final
2. Interviewer role: Recruiter / Hiring Manager / Senior IC / Panel
3. Interview date (if known — leave blank if not)

Wait for answers before proceeding.

## Step 2 — Pull context from Notion
Fetch the Notion page at $ARGUMENTS. Extract:
- Company name, role title, location
- Full JD text (from ## Job Description section)
- Tailored resume text (from ## Tailored Resume section, if present)
- Archetype detection (from ## Archetype Detection section)
- Notes (match rationale, flags, comp range)

## Step 3 — Load STAR library
Read `skills/star-library.md`. Index all stories by theme so they can be matched to questions in Step 5.

## Step 4 — Generate likely questions
Based on the interview type and JD competencies, generate 6–8 questions most likely to be asked.

For behavioural questions, map each to the closest story theme from the STAR library before writing any answers.

## Step 5 — Write answers
**Tone rule — non-negotiable:**
Write every answer as a natural spoken narrative. The goal is a story you would tell across a table to someone you respect — not a structured recital of Situation / Task / Action / Result labels.

- Use existing stories from `skills/star-library.md` as the primary source. If a story fits at 70%+ relevance, use it.
- Light adaptation for company context is fine: change the framing, emphasise the angle most relevant to this role, adjust the opening hook.
- Do not inject JD keywords. If a skill or tool is genuinely part of the story, it stays. If it isn't, it's cut.
- Do not fabricate metrics or experiences. Every number must be in `context/profile.md` Resume Metrics Reference.
- Every answer must hold up under 20 minutes of follow-up questions.
- Target 90–120 seconds when spoken aloud.

For each answer, add a **Landing guidance** note (2–3 bullets, not part of the spoken answer):
- What to lead with for this specific company
- Which metric to land on hardest
- What to add if they ask to go deeper

## Step 6 — Company research
Research the company across four areas:
1. Core business model and main products/services
2. Main competitors and how this company is positioned
3. How the specific team/function this role sits in drives revenue
4. Most recent developments — news, product launches, financial results, leadership changes

Write a 3–4 sentence "Why this company" answer from this research. It must reference something specific — a product decision, a market move, a team priority — not generic admiration.

Include a **Company Research** section in the prep sheet with all four areas in full, even details that don't make the spoken answer. Useful when follow-up questions go sideways.

## Step 7 — Questions to ask
Generate 4–5 smart questions to ask the interviewer. Tailored to the role and company:
- One about the lifecycle/CRM stack or experimentation maturity
- One about the team's current focus or biggest challenge
- One about what success looks like in the first 6 months
- One showing you've thought about their specific product or market challenge

## Step 8 — Save to file
Save the full prep sheet to `working/interview_prep_[COMPANY]_$(date +%Y-%m-%d).md`.

## Step 9 — Create Notion sub-page
Create a new Notion page as a child of the job tracker page at $ARGUMENTS:
- Title: `Interview Prep — [INTERVIEW_TYPE] — [DATE]`
- Populate with the full prep content using the structure in `agents/interview-prepper.md`

Then append a link to the new sub-page at the bottom of the parent tracker page under `## Interview Prep`.

If the tracker row Status is "To Apply" or "Applied", update it to "Interview Scheduled".

## Step 10 — Confirm
Print:
```
✓ Prep saved: working/interview_prep_[COMPANY]_[DATE].md
✓ Notion sub-page created and linked to tracker row
✓ Status updated to: Interview Scheduled
```
