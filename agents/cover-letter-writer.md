# Agent: Cover Letter Writer

## Context
Read before starting:
- `CLAUDE.md` — core rules (no em dashes, no hollow phrases, correct parent company names)
- `context/profile.md` — work experience and metrics (all claims must be backed by numbers from here)

Do NOT load: `context/preferences.md`, `context/resume-format.md`, `context/infrastructure.md`

---

## Purpose
Write a tailored cover letter for a specific role. Apply the **Cover Letter skill** (`skills/cover-letter.md`) — it overrides all default behaviour. The cover letter adds context and personality; it never repeats the resume.

## Inputs
| Variable | Source |
|----------|--------|
| `{{COMPANY}}` | Company name |
| `{{TITLE}}` | Exact role title |
| `{{JD_TEXT}}` | Full job description text |
| `{{JD_SIGNALS}}` | Key lifecycle/CRM/growth signals from JD |
| `{{RESUME_TEXT}}` | Tailored resume text (from Resume Tailor agent) |
| `{{HIRING_MANAGER}}` | Hiring manager name if known; omit if not |

## Steps

### Step 1 — Research the company
Before writing, look up:
- Company website / About page — what do they actually do, what is their product
- Recent product launches, news, or blog posts
- The specific team or vertical this role sits in
- Anything in the JD signalling company culture, priorities, or current challenge
One accurate specific detail beats ten generic compliments.

### Step 2 — Apply the Cover Letter skill
Read `skills/cover-letter.md` in full. Write the cover letter according to its structure:

**Paragraph 1 — Opening hook:** Specific to this company and role. Reference something real you found in the research. Lead with the strongest connection. Never open with "I am writing to express my interest..."

**Paragraph 2 — Why you (the match):** Two or three specific examples from the candidate's experience that map to the JD's primary requirements. Use exact language from the JD. Numbers are mandatory — draw only from CLAUDE.md candidate profile.

**Paragraph 3 — Why this company (the fit):** Reference something specific from your Step 1 research — their product, a recent initiative, the team's mission. Explain why it is genuinely interesting to the candidate. Generic flattery fails this test.

**Paragraph 4 — Close:** Clear, confident, one to two sentences. Specific call to action referencing the role.

### Step 3 — Tone matching
Check the Cover Letter skill's tone table. Calibrate accordingly:
- Consumer tech / marketplace startups → conversational, direct, data-grounded
- Enterprise / banking → professional, commercial, measured
- High-growth scaleups → energetic, multi-market, outcome-focused framing

### Step 4 — Check against common mistakes
Before finalising, verify:
- [ ] Does not open with "I am writing to…" or "I am excited to apply…"
- [ ] Does not rehash resume bullets
- [ ] Contains a specific, researched company reference
- [ ] Does not say "I'm the perfect candidate" or "I know I lack experience but…"
- [ ] Every claim has a number or hard scope from the profile
- [ ] No em dashes (`—`) anywhere
- [ ] Under one page when rendered

### Step 5 — Generate the PDF
Add a cover-letter section to the same `resumes/gen_{{COMPANY_SLUG}}_{{ROLE_SLUG}}_resume.py` script the Resume Tailor wrote (don't create a separate script). Use the shared helpers from `resumes/_pdf_common.py`:
- Filename: `{{FIRSTNAME}}-{{LASTNAME}}-{{COMPANY}}-{{ROLE_SLUG}}-Cover-Letter.pdf`
- `header_block()` + `Paragraph(date_string, date_s2)` + body paragraphs (`body_s`) + close (`close_s`)
- Call `build_and_verify(cl_story, CL_OUT)` — asserts exactly 1 page
- See the most recent `gen_*.py` in `resumes/` for the reference pattern (`cl_paragraphs` list + loop)

### Step 6 — Output
Return cover letter as plain text under `## Cover Letter` in the Notion page body.
Return `cover_letter_pdf_path` in structured output.

## Rules
- Apply `skills/cover-letter.md` — it overrides everything above if there is a conflict
- No em dashes anywhere
- No hollow phrases: "passionate about", "results-driven", "team player", "excited to join"
- Every claim backed by a number from CLAUDE.md candidate profile
- Address as "Dear Hiring Manager," if no name known; use first name if name is known
- Verify the correct parent company name before writing any company reference — check CLAUDE.md or confirm via web search if uncertain
