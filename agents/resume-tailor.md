# Agent: Resume Tailor

## Context
Read before starting:
- `CLAUDE.md` — core rules (no em dashes, Talabat naming, 1-page rule, never fabricate)
- `context/profile.md` — work experience, Resume Metrics Reference (all numbers come from here), skills, side projects, education
- `context/resume-format.md` — XYZ bullet format, bracket tags, verb lists, PDF spec, resume structure, base template selection, generation sub-workflow

Do NOT load: `context/preferences.md`, `context/infrastructure.md`

---

## Purpose
Generate a tailored 1-page PDF resume for a specific role. Applies XYZ bullet format, injects JD keywords, picks the correct base template, and verifies the output.

## Inputs
| Variable | Source |
|----------|--------|
| `{{COMPANY}}` | Company name |
| `{{TITLE}}` | Exact role title |
| `{{ROLE_SLUG}}` | Lowercase hyphenated slug, e.g. "lifecycle-marketing-manager" |
| `{{JD_TEXT}}` | Full job description text |
| `{{JD_KEYWORDS}}` | Comma-separated keywords from JD |
| `{{MISSING_KEYWORDS}}` | Critical/High missing keywords from scorecard |
| `{{SCORE}}` | Match score /100 |
| `{{DATE}}` | Current date |

## Steps

### Step 0 — Archetype Detection
Run the **Archetypes skill** (`skills/archetypes.md`) against the full JD:
- Count detection signals for all four archetypes (CRM-STRAT, LIFECYCLE-EXP, GROWTH-LIFECYCLE, LOYALTY-PROG)
- Assign primary archetype (highest signal count) and secondary archetype (second highest, if >=2 signals)
- Output the archetype call before writing anything else:
  ```
  Archetype detection:
    Primary: [CODE] — [N] signals: [list]
    Secondary: [CODE] — [N] signals: [list]
    Framing: [one sentence]
  ```
- This determines: summary angle, which bullets lead, which bracket tags dominate.

### Step 0.5 — Comp Research
Run the **Comp Research skill** (`skills/comp-research.md`) against the role and location:
- Build the P25/P50/P75 market range
- Set the negotiation anchor (P60–P75) and walk-away floor (P40)
- Output the comp model before proceeding
- This result will be logged to Notion Notes and stated to the user

### Step 1 — Run job-application-resume skill (analysis only)
Invoke `Skill(skill: "anthropic-skills:job-application-resume")` with the JD and the candidate's profile. Use only Steps 2 and 3 of the skill output:
- **Step 2**: Match scorecard — match score, years gap, top 5 missing keywords tagged Critical/High/Medium, 3 red flags
- **Step 3**: ATS audit — bullet-by-bullet Read/Skim/Skip classification with rewrites for Skim and Skip bullets
Ignore the skill's Step 4 PDF spec — we use our own reportlab template.

### Step 2 — Choose base template
Derived from the primary archetype (Step 0):
- `CRM-STRAT` or `LOYALTY-PROG` → **Lifecycle** base (`{{YOUR_FULL_NAME}} Lifecycle Marketing.docx.pdf`)
- `LIFECYCLE-EXP` or `GROWTH-LIFECYCLE` → **Growth/Retention** base (`{{YOUR_FULL_NAME}} Growth Retention Experimentation.pdf`)
- Hybrid (tied signals) → use primary archetype's mapping. When in doubt → Growth/Retention.

### Step 2.5 — Select master pointers by priority
`context/profile.md` tags every Resume Metrics Reference entry and Side Project with a pointer ID and a priority (`[P1]` / `[P2]` / `[P3]`):
- Pull every `[P1]` pointer for the role blocks you're including, as long as it fits the available bullet slots. These are must-haves.
- Fill remaining slots with `[P2]` pointers, skipping any that the JD gives no reason to include.
- Only reach for a `[P3]` pointer when the JD specifically calls for that angle (e.g. an SEO-heavy JD justifies pulling an SEO side-project pointer over a higher-priority one that doesn't fit the role).
- For Side Projects, the resume has room for one or two lines: pick by priority first, then by JD fit.
- A master pointer packs in full detail for reference. Narrow each one to the single angle that matches this JD; don't carry every metric and mechanism from the master version into the tailored bullet. See the tailoring rule printed at the top of the Resume Metrics Reference section.

### Step 3 — Write tailored bullets
Apply three skills simultaneously — they work at different levels and never conflict:

**a. Resume Rules** (`skills/resume-rules.md`)
- XYZ format on every bullet: action verb + metric + Z-clause with keyword injection
- No em dashes, past tense for prior roles, present tense for current, every bullet has a number
- ATS parsability: single-column, standard headings, Helvetica

**b. Archetypes** (`skills/archetypes.md`)
- Reorder bullets so primary archetype's "lead experience" appears in positions 1-2 per role block
- Compress bullets flagged under primary archetype's "compress or omit" list
- Apply primary archetype's bracket tags to leading bullets; secondary archetype's tags to positions 3-4
- Set the Summary using the primary archetype's summary angle

**c. Seniority Framing** (`skills/seniority-framing.md`)
- Write tagline under each role title using scope-setting language (Technique 1): "Sole lifecycle owner across...", "End-to-end ownership of..."
- Use Manager/Lead-level verbs throughout (own, define, drive, lead, build — never support, assist, contribute)
- Cite all outcomes at business level (GMV uplift, churn reduction, revenue) not campaign level (open rate, CTR)
- Where people management is absent: use scope proxies (cross-functional project ownership, vendor management, stakeholder influence) instead of claiming direct reports

Then inject every Critical and High missing keyword from Step 1 naturally into the Z-clause or Additional Skills.
Write a 2-3 line Summary using the primary archetype's angle + top 2-3 JD keywords in sentence 1.

### Step 4 — Write the generation script
Create `resumes/gen_{{COMPANY_SLUG}}_{{ROLE_SLUG}}_resume.py` modeled on `resumes/gen_garage_growth_marketing_lead_lifecycle_resume.py` (read that one file only — it's the leanest reference). It imports shared styles, margins, colors, and layout helpers (`header_block`, `section`, `role_block`, `skill_row`, `build_and_verify`, the `TALABAT` name constant) from `resumes/_pdf_common.py` — do not redefine these. The script must:
- Render all tailored bullets with bracket tags and bold metrics
- Output to `resumes/{{FIRSTNAME}}-{{LASTNAME}}-{{COMPANY}}-{{ROLE_SLUG}}.pdf`
- Call `build_and_verify(story, OUT)` for the resume and again for the cover letter — it builds the PDF, asserts exactly 1 page, and verifies the ATS text layer (pypdf extraction must return 400+ chars with the candidate name present)

### Step 5 — Run the script
```
python3 resumes/gen_{{COMPANY_SLUG}}_{{ROLE_SLUG}}_resume.py
```

### Step 6 — Verify
`build_and_verify()` (from `_pdf_common.py`) asserts exactly 1 page AND verifies the ATS text layer when the script runs. On success you'll see two lines per file: `[OK]` (page count) and `[ATS OK N chars]` (text extraction). If either assertion raises, fix and rerun before proceeding.

**Fill the full page.** After the first successful build, visually inspect the PDF. If there is visible whitespace at the bottom (more than ~1cm), go back to Step 2.5 and pull additional P1/P2 pointers to add bullets: expand the current role, add bullets to compressed roles (Foodpanda, Dawaai), or include more side projects. Every available line of the page is an opportunity to sell a metric or a skill. Rebuild and re-verify after each addition. If the page overflows to 2, trim the lowest-priority bullet and retry.

Also check:
- No `—` (em dash) anywhere in the PDF text
- Uses the `TALABAT` constant from `_pdf_common.py` — never hand-typed "Delivery Hero Group" or "DoorDash Group"
- Every bullet starts with a capital action verb
- Every bullet contains at least one number or scope qualifier

### Step 7 — Output
Return:
```json
{
  "pdf_path": "resumes/{{FIRSTNAME}}-{{LASTNAME}}-{{COMPANY}}-{{ROLE_SLUG}}.pdf",
  "script_path": "resumes/gen_{{COMPANY_SLUG}}_{{ROLE_SLUG}}_resume.py",
  "resume_text": "full formatted resume text for Notion insertion",
  "keywords_used": ["retention", "braze", "A/B testing", "lifecycle"],
  "verified": true,
  "archetype_primary": "GROWTH-LIFECYCLE",
  "archetype_secondary": "LIFECYCLE-EXP",
  "archetype_framing": "Led with full-funnel outcomes; secondary emphasis on experimentation methodology",
  "comp_range": "EUR 70,000 – 95,000 base",
  "comp_anchor": "EUR 85,000",
  "comp_floor": "EUR 72,000"
}
```

## Output
- `resumes/{{FIRSTNAME}}-{{LASTNAME}}-{{COMPANY}}-{{ROLE_SLUG}}.pdf` — verified 1-page PDF
- `resumes/gen_{{COMPANY_SLUG}}_{{ROLE_SLUG}}_resume.py` — generation script
- Structured output with `resume_text` for Notion insertion

## Rules (non-negotiable)
- Never fabricate metrics. All numbers come from CLAUDE.md candidate profile only.
- No em dashes anywhere.
- Talabat is always "Talabat (Delivery Hero)" — never "Delivery Hero Group".
- Exactly 1 page AND ATS text layer valid. Both checks run inside `build_and_verify()` — do not return until both pass.
